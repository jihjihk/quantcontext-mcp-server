"""Maps pipeline spec stages to deterministic skill functions and executes sequentially."""
from __future__ import annotations

import pandas as pd

from quantcontext.engine.data import get_universe
from quantcontext.engine.skills.pipeline_skills.registry import SKILL_REGISTRY


def execute_pipeline(
    pipeline: dict,
    date: str,
    *,
    _universe_cache: dict | None = None,
    _prices: pd.DataFrame | None = None,
) -> tuple[list[dict], pd.DataFrame]:
    """Run all pipeline stages in order.

    Args:
        _universe_cache: Optional dict used as a mutable cache for the base
            universe DataFrame (before price enrichment).  When provided, the
            expensive ``get_universe(fundamentals=True)`` call is executed only
            once and reused on subsequent invocations.  Callers that run the
            pipeline many times (e.g. the backtest loop) should pass a single
            ``{}`` dict that persists across calls.

    Returns:
        results: list of per-stage result dicts (input_count, output_count, sample, etc.)
        candidates: final DataFrame after all stages
    """
    universe_name = pipeline.get("universe", "sp500")
    stages = sorted(pipeline.get("stages", []), key=lambda s: s.get("order", 0))

    # Avoid 500+ per-ticker yfinance calls when no stage needs fundamental data.
    # Price-only screens (momentum, technical_signal, mean_reversion) set
    # needs_fundamentals=False in their SKILL_META; all others default to True.
    needs_fundamentals = any(
        SKILL_REGISTRY.get(s.get("skill", ""), {}).get("meta", {}).get("needs_fundamentals", True)
        for s in stages
    )

    needs_price_enrichment = any(
        SKILL_REGISTRY.get(s.get("skill", ""), {}).get("meta", {}).get("needs_price_enrichment", True)
        for s in stages
    )

    if _universe_cache is not None and "base" in _universe_cache:
        # Reuse cached fundamentals, only re-enrich with price data for this date
        if needs_price_enrichment:
            from quantcontext.engine.data import enrich_with_price_data
            candidates = enrich_with_price_data(_universe_cache["base"].copy(), date, prices=_prices)
        else:
            candidates = _universe_cache["base"].copy()
    else:
        candidates = get_universe(date, universe_name, fundamentals=needs_fundamentals, enrich=needs_price_enrichment, prices=_prices)
        if _universe_cache is not None and needs_fundamentals:
            # Cache the fundamentals-only DataFrame (before price enrichment)
            # by stripping the price-derived columns that change per date
            price_cols = [
                "return_21d", "return_63d", "return_126d", "return_252d",
                "volatility_20d", "rsi_14", "sma_50", "sma_200",
                "bb_position", "z_score_60d",
            ]
            _universe_cache["base"] = candidates.drop(
                columns=[c for c in price_cols if c in candidates.columns]
            )

    results: list[dict] = []

    for stage in stages:
        skill_id = stage["skill"]
        if skill_id not in SKILL_REGISTRY:
            raise KeyError(f"Unknown pipeline skill: '{skill_id}'")

        skill = SKILL_REGISTRY[skill_id]
        input_count = len(candidates)
        input_tickers = set(candidates["ticker"].tolist()) if "ticker" in candidates.columns else set()

        output = skill["run"](candidates, stage.get("config", {}), date)
        output_count = len(output)

        sample = output.head(5).to_dict("records") if len(output) > 0 else []

        if "ticker" in output.columns and "ticker" in candidates.columns:
            output_tickers = set(output["ticker"].tolist())
            removed_tickers = input_tickers - output_tickers
            removed = candidates[candidates["ticker"].isin(removed_tickers)].head(5).to_dict("records")
        else:
            removed = []

        results.append({
            "stage": stage,
            "input_count": input_count,
            "output_count": output_count,
            "sample": sample,
            "removed_sample": removed,
        })

        candidates = output

    return results, candidates
