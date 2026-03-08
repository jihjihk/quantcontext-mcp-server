#!/usr/bin/env python3
"""
Reproduce the equity_curve truncation bug across 10 diverse strategies.

Uses the same mock data layer as tests (conftest.py) so no yfinance calls.
Run: .venv/bin/python scripts/test_equity_curve_bug.py
"""
import asyncio
import json
import sys
import os
from unittest.mock import patch

# Add src and tests to path
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

# Import mock builders from conftest
from conftest import _fetch_prices, _get_universe, _get_factors

from quantcontext.server import backtest_strategy, factor_analysis


# All dates within the mock data range (2023-01-01 to 2024-12-31)
STRATEGIES = [
    {
        "name": "1. Value (sp500, monthly, 1yr)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "value_screen", "config": {"top_n": 10}}],
            "universe": "sp500", "rebalance": "monthly",
            "start_date": "2023-06-01", "end_date": "2024-06-01",
        },
    },
    {
        "name": "2. Momentum (nasdaq100, monthly, 1yr)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "momentum_screen", "config": {"lookback_days": 200, "top_pct": 20}}],
            "universe": "nasdaq100", "rebalance": "monthly",
            "start_date": "2023-06-01", "end_date": "2024-06-01",
        },
    },
    {
        "name": "3. Fundamental (sp500, weekly, 1yr)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "fundamental_screen", "config": {"pe_lt": 15, "roe_gt": 12}}],
            "universe": "sp500", "rebalance": "weekly",
            "start_date": "2023-06-01", "end_date": "2024-06-01",
        },
    },
    {
        "name": "4. Quality (sp500, monthly, 18mo)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "quality_screen", "config": {"roe_gt": 15, "debt_equity_lt": 1.0}}],
            "universe": "sp500", "rebalance": "monthly",
            "start_date": "2023-01-01", "end_date": "2024-06-30",
        },
    },
    {
        "name": "5. Factor model (sp500, monthly, 1yr)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "factor_model", "config": {"weights": {"value": 0.4, "momentum": 0.3, "quality": 0.3}, "top_n": 15}}],
            "universe": "sp500", "rebalance": "monthly",
            "start_date": "2023-06-01", "end_date": "2024-06-01",
        },
    },
    {
        "name": "6. Technical (nasdaq100, weekly, 1yr)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "technical_signal", "config": {"rsi_period": 14, "sma_short": 50, "sma_long": 200}}],
            "universe": "nasdaq100", "rebalance": "weekly",
            "start_date": "2023-06-01", "end_date": "2024-06-01",
        },
    },
    {
        "name": "7. Mean reversion (sp500, daily, 6mo)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "mean_reversion", "config": {"lookback_days": 60, "z_threshold": -1.5}}],
            "universe": "sp500", "rebalance": "daily",
            "start_date": "2024-01-01", "end_date": "2024-06-30",
        },
    },
    {
        "name": "8. Value top_n=1 (sp500, daily, 1yr)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "value_screen", "config": {"top_n": 1}}],
            "universe": "sp500", "rebalance": "daily",
            "start_date": "2023-06-01", "end_date": "2024-06-01",
        },
    },
    {
        "name": "9. Momentum (sp500, monthly, 18mo)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "momentum_screen", "config": {"lookback_days": 120, "top_pct": 10}}],
            "universe": "sp500", "rebalance": "monthly",
            "start_date": "2023-01-01", "end_date": "2024-06-30",
        },
    },
    {
        "name": "10. Quality (nasdaq100, weekly, 6mo)",
        "kwargs": {
            "stages": [{"order": 1, "type": "screen", "skill": "quality_screen", "config": {"roe_gt": 20}}],
            "universe": "nasdaq100", "rebalance": "weekly",
            "start_date": "2024-01-01", "end_date": "2024-06-30",
        },
    },
]


async def run_one(strategy: dict) -> dict:
    name = strategy["name"]
    try:
        bt_raw = await backtest_strategy(**strategy["kwargs"])
        bt = json.loads(bt_raw)

        if "error" in bt:
            return {"name": name, "status": "BACKTEST_ERROR", "error": bt["error"]}

        ec = bt.get("equity_curve", [])
        truncated = bt.get("truncated", False)
        raw_len = len(bt_raw)

        # Try factor analysis with the returned equity_curve
        fa_status = "N/A"
        fa_error = None
        fa_alpha = None
        try:
            fa_raw = await factor_analysis(equity_curve=ec)
            fa = json.loads(fa_raw)
            if "error" in fa:
                fa_status = fa.get("code", "ERROR")
                fa_error = fa["error"]
            else:
                fa_status = "OK"
                fa_alpha = fa.get("alpha_annualized")
        except Exception as e:
            fa_status = "EXCEPTION"
            fa_error = str(e)

        return {
            "name": name,
            "status": "OK",
            "response_chars": raw_len,
            "truncated": truncated,
            "equity_curve_points": len(ec),
            "fa_status": fa_status,
            "fa_error": fa_error,
            "fa_alpha": fa_alpha,
        }
    except Exception as e:
        return {"name": name, "status": "EXCEPTION", "error": str(e)}


async def main():
    print("=" * 90)
    print("EQUITY CURVE TRUNCATION BUG REPRODUCER (using mock data layer)")
    print("=" * 90)
    print()

    results = []
    for s in STRATEGIES:
        print(f"Running: {s['name']}...", flush=True)
        r = await run_one(s)
        results.append(r)
        if r["status"] == "OK":
            print(f"  Response: {r['response_chars']:,} chars | "
                  f"EC points: {r['equity_curve_points']} | "
                  f"Truncated: {r['truncated']} | "
                  f"FA: {r['fa_status']}")
            if r["fa_error"]:
                print(f"  FA error: {r['fa_error']}")
        else:
            print(f"  {r['status']}: {r.get('error', 'unknown')}")
        print()

    # Summary table
    print()
    print("=" * 90)
    print(f"{'Strategy':<42} {'Chars':>8} {'EC pts':>7} {'Trunc':>6} {'FA status':>16}")
    print("-" * 90)
    for r in results:
        if r["status"] == "OK":
            print(f"{r['name']:<42} {r['response_chars']:>8,} {r['equity_curve_points']:>7} "
                  f"{'YES' if r['truncated'] else 'no':>6} {r['fa_status']:>16}")
        else:
            print(f"{r['name']:<42} {'ERR':>8} {'--':>7} {'--':>6} {r['status']:>16}")

    # Verdict
    print()
    truncated_count = sum(1 for r in results if r.get("truncated"))
    fa_fail_count = sum(1 for r in results if r.get("fa_status") in ("REGRESSION_ERROR", "ERROR", "EXCEPTION"))
    print(f"Truncated: {truncated_count}/{len(results)}")
    print(f"Factor analysis failed: {fa_fail_count}/{len(results)}")
    if truncated_count > 0:
        print("\nCONFIRMED: equity_curve truncation breaks the backtest -> factor_analysis pipeline")
    if fa_fail_count > 0 and truncated_count == 0:
        print("\nFactor analysis failures NOT caused by truncation — investigate other causes")


if __name__ == "__main__":
    with (
        patch("quantcontext.engine.backtest_engine.fetch_prices", side_effect=_fetch_prices),
        patch("quantcontext.engine.pipeline_executor.get_universe", side_effect=_get_universe),
        patch("quantcontext.engine.factor_analysis.get_factors", side_effect=_get_factors),
    ):
        asyncio.run(main())
