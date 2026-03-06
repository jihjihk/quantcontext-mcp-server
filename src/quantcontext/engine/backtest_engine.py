"""Deterministic rebalance-loop backtester.

Executes a pipeline on each rebalance date, sizes positions,
tracks daily P&L, and computes standard metrics.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from quantcontext.engine.data import fetch_prices
from quantcontext.engine.pipeline_executor import execute_pipeline


def _rebalance_dates(start: str, end: str, freq: str) -> list[pd.Timestamp]:
    """Generate rebalance dates within the range."""
    freq_map = {"daily": "B", "weekly": "W-FRI", "monthly": "MS", "quarterly": "QS"}
    pd_freq = freq_map.get(freq, "MS")
    dates = pd.date_range(start, end, freq=pd_freq)
    return list(dates)


def _equal_weight(candidates: pd.DataFrame) -> dict[str, float]:
    """Equal-weight across all candidates."""
    tickers = candidates["ticker"].tolist()
    if not tickers:
        return {}
    w = 1.0 / len(tickers)
    return {t: w for t in tickers}


def _inverse_vol_weight(candidates: pd.DataFrame, prices: pd.DataFrame, date: pd.Timestamp) -> dict[str, float]:
    """Weight by inverse 20-day realized volatility."""
    tickers = candidates["ticker"].tolist()
    available = [t for t in tickers if t in prices.columns]
    if not available:
        return {}

    lookback = prices.loc[:date].tail(21)
    if len(lookback) < 5:
        return _equal_weight(candidates)

    rets = lookback[available].pct_change().dropna()
    vols = rets.std()
    vols = vols.replace(0, np.nan).fillna(vols.median())

    inv_vol = 1.0 / vols
    total = inv_vol.sum()
    if total == 0:
        return _equal_weight(candidates)

    weights = (inv_vol / total).to_dict()
    return {t: weights.get(t, 0) for t in available}


def _enforce_limits(weights: dict[str, float], risk_limits: dict) -> dict[str, float]:
    """Enforce position size caps. Redistribute excess pro-rata."""
    max_pos = risk_limits.get("max_position_size")
    if not max_pos or not weights:
        return weights

    capped = {}
    excess = 0.0
    uncapped_tickers = []

    for t, w in weights.items():
        if w > max_pos:
            capped[t] = max_pos
            excess += w - max_pos
        else:
            capped[t] = w
            uncapped_tickers.append(t)

    # Redistribute excess to uncapped positions
    if excess > 0 and uncapped_tickers:
        uncapped_total = sum(capped[t] for t in uncapped_tickers)
        if uncapped_total > 0:
            for t in uncapped_tickers:
                capped[t] += excess * (capped[t] / uncapped_total)

    return capped


def run_backtest(pipeline: dict, config: dict) -> dict:
    """Run a deterministic backtest.

    Args:
        pipeline: Pipeline spec with stages, universe, risk_limits
        config: {start_date, end_date, initial_capital, rebalance, sizing}

    Returns:
        {equity_curve, trades, metrics, holdings_over_time, stage_results_by_date}
    """
    start = config.get("start_date", "2023-01-01")
    end = config.get("end_date", "2025-12-31")
    initial_capital = config.get("initial_capital", 100000)
    freq = config.get("rebalance", "monthly")
    sizing = config.get("sizing", "equal_weight")
    risk_limits = pipeline.get("risk_limits", {})
    stop_loss = risk_limits.get("stop_loss")
    max_dd = risk_limits.get("max_drawdown")

    rebal_dates = _rebalance_dates(start, end, freq)
    if not rebal_dates:
        return {"equity_curve": [], "trades": [], "metrics": {}, "holdings_over_time": [], "stage_results_by_date": {}}

    # Run pipeline once to discover tickers we'll need prices for
    _, initial_candidates = execute_pipeline(pipeline, rebal_dates[0].strftime("%Y-%m-%d"))
    all_tickers = initial_candidates["ticker"].tolist() if "ticker" in initial_candidates.columns else []

    # Expand: run pipeline on a few dates to discover all possible tickers
    for rd in rebal_dates[:3]:
        _, cands = execute_pipeline(pipeline, rd.strftime("%Y-%m-%d"))
        if "ticker" in cands.columns:
            all_tickers.extend(cands["ticker"].tolist())
    all_tickers = sorted(set(all_tickers))

    if not all_tickers:
        return {"equity_curve": [], "trades": [], "metrics": {}, "holdings_over_time": [], "stage_results_by_date": {}}

    # Fetch all prices at once
    prices = fetch_prices(all_tickers, start, end)

    # Trading dates = all business days where we have price data
    trading_dates = prices.index.sort_values()
    if trading_dates.empty:
        return {"equity_curve": [], "trades": [], "metrics": {}, "holdings_over_time": [], "stage_results_by_date": {}}

    # State
    cash = float(initial_capital)
    positions: dict[str, float] = {}  # ticker -> number of shares
    entry_prices: dict[str, float] = {}  # ticker -> entry price (for stop-loss)
    equity_curve: list[dict] = []
    trades: list[dict] = []
    holdings_over_time: list[dict] = []
    stage_results_by_date: dict[str, list[dict]] = {}
    peak_value = float(initial_capital)
    in_cash_circuit_breaker = False

    rebal_set = set(rebal_dates)

    for date in trading_dates:
        date_str = date.strftime("%Y-%m-%d")

        # Current portfolio value
        portfolio_value = cash
        for ticker, shares in positions.items():
            if ticker in prices.columns and date in prices.index:
                price = prices.loc[date, ticker]
                if pd.notna(price):
                    portfolio_value += shares * float(price)

        # Track peak and drawdown
        if portfolio_value > peak_value:
            peak_value = portfolio_value
        current_dd = (portfolio_value - peak_value) / peak_value if peak_value > 0 else 0

        # Circuit breaker: if max drawdown exceeded, go to cash
        if max_dd and current_dd < -abs(max_dd) and not in_cash_circuit_breaker:
            in_cash_circuit_breaker = True
            for ticker, shares in list(positions.items()):
                if ticker in prices.columns and date in prices.index:
                    price = float(prices.loc[date, ticker])
                    if pd.notna(price):
                        cash += shares * price
                        trades.append({"date": date_str, "ticker": ticker, "action": "SELL",
                                       "shares": shares, "price": price, "weight": 0, "reason": "circuit_breaker"})
            positions = {}
            entry_prices = {}

        # Stop-loss check (daily)
        if stop_loss and not in_cash_circuit_breaker:
            for ticker in list(positions.keys()):
                if ticker in prices.columns and date in prices.index and ticker in entry_prices:
                    price = float(prices.loc[date, ticker])
                    if pd.notna(price):
                        ret = (price - entry_prices[ticker]) / entry_prices[ticker]
                        if ret < -abs(stop_loss):
                            shares = positions.pop(ticker)
                            cash += shares * price
                            entry_prices.pop(ticker, None)
                            trades.append({"date": date_str, "ticker": ticker, "action": "SELL",
                                           "shares": shares, "price": price, "weight": 0, "reason": "stop_loss"})

        # Rebalance
        if date in rebal_set and not in_cash_circuit_breaker:
            stage_results, candidates = execute_pipeline(pipeline, date_str)
            stage_results_by_date[date_str] = stage_results

            if "ticker" not in candidates.columns or len(candidates) == 0:
                continue

            # Size positions
            if sizing == "inverse_volatility":
                target_weights = _inverse_vol_weight(candidates, prices, date)
            else:
                target_weights = _equal_weight(candidates)

            target_weights = _enforce_limits(target_weights, risk_limits)

            # Liquidate positions not in target
            for ticker in list(positions.keys()):
                if ticker not in target_weights:
                    if ticker in prices.columns and date in prices.index:
                        price = float(prices.loc[date, ticker])
                        if pd.notna(price):
                            cash += positions[ticker] * price
                            trades.append({"date": date_str, "ticker": ticker, "action": "SELL",
                                           "shares": positions[ticker], "price": price, "weight": 0, "reason": "rebalance"})
                    positions.pop(ticker)
                    entry_prices.pop(ticker, None)

            # Recompute portfolio value after sells
            portfolio_value = cash
            for ticker, shares in positions.items():
                if ticker in prices.columns and date in prices.index:
                    price = float(prices.loc[date, ticker])
                    if pd.notna(price):
                        portfolio_value += shares * price

            # Buy/adjust to target weights
            for ticker, weight in target_weights.items():
                if ticker not in prices.columns or date not in prices.index:
                    continue
                price = float(prices.loc[date, ticker])
                if pd.isna(price) or price <= 0:
                    continue

                target_value = portfolio_value * weight
                current_shares = positions.get(ticker, 0)
                current_value = current_shares * price
                diff_value = target_value - current_value

                if abs(diff_value) < 1.0:  # ignore tiny adjustments
                    continue

                diff_shares = diff_value / price
                if diff_shares > 0:
                    # Buy
                    positions[ticker] = current_shares + diff_shares
                    cash -= diff_shares * price
                    entry_prices[ticker] = price
                    trades.append({"date": date_str, "ticker": ticker, "action": "BUY",
                                   "shares": round(diff_shares, 4), "price": round(price, 2),
                                   "weight": round(weight, 4), "reason": "rebalance"})
                elif diff_shares < 0:
                    # Trim
                    sell_shares = min(abs(diff_shares), current_shares)
                    positions[ticker] = current_shares - sell_shares
                    cash += sell_shares * price
                    if positions[ticker] <= 0:
                        positions.pop(ticker)
                        entry_prices.pop(ticker, None)
                    trades.append({"date": date_str, "ticker": ticker, "action": "SELL",
                                   "shares": round(sell_shares, 4), "price": round(price, 2),
                                   "weight": round(weight, 4), "reason": "rebalance"})

            # Record holdings
            holdings = {}
            for ticker, shares in positions.items():
                if ticker in prices.columns and date in prices.index:
                    price = float(prices.loc[date, ticker])
                    if pd.notna(price):
                        holdings[ticker] = round(shares * price / portfolio_value, 4)
            holdings_over_time.append({"date": date_str, "weights": holdings})

        # Record equity
        portfolio_value = cash
        for ticker, shares in positions.items():
            if ticker in prices.columns and date in prices.index:
                price = prices.loc[date, ticker]
                if pd.notna(price):
                    portfolio_value += shares * float(price)

        equity_curve.append({"date": date_str, "value": round(float(portfolio_value), 2)})

    # Compute metrics
    metrics = _compute_metrics(equity_curve, initial_capital, trades)

    return {
        "equity_curve": equity_curve,
        "trades": trades,
        "metrics": metrics,
        "holdings_over_time": holdings_over_time,
        "stage_results_by_date": stage_results_by_date,
    }


def _compute_metrics(equity_curve: list[dict], initial_capital: float, trades: list[dict]) -> dict:
    """Compute standard backtest metrics from an equity curve."""
    if not equity_curve:
        return {}

    values = pd.Series([e["value"] for e in equity_curve], dtype=float)
    daily_returns = values.pct_change().dropna()

    total_return = (values.iloc[-1] / initial_capital - 1)
    n_years = len(values) / 252
    cagr = (values.iloc[-1] / initial_capital) ** (1 / max(n_years, 0.01)) - 1 if n_years > 0 else 0

    # Sharpe (assuming 0 risk-free rate for simplicity)
    sharpe = float(np.sqrt(252) * daily_returns.mean() / max(daily_returns.std(), 1e-10)) if len(daily_returns) > 1 else 0

    # Max drawdown
    rolling_max = values.cummax()
    drawdown = (values - rolling_max) / rolling_max
    max_drawdown = float(drawdown.min())

    # Calmar
    calmar = float(cagr / abs(max_drawdown)) if max_drawdown != 0 else 0

    # Daily win rate: fraction of days with positive returns
    buy_trades = [t for t in trades if t["action"] == "BUY"]
    sell_trades = [t for t in trades if t["action"] == "SELL"]
    daily_win_rate = 0.0
    if buy_trades and sell_trades:
        daily_win_rate = float((daily_returns > 0).mean())

    # Turnover: total traded value / avg portfolio value
    total_traded = sum(abs(t.get("shares", 0) * t.get("price", 0)) for t in trades)
    avg_value = values.mean()
    turnover = float(total_traded / avg_value / max(n_years, 0.01)) if avg_value > 0 else 0

    return {
        "total_return": round(float(total_return), 4),
        "cagr": round(float(cagr), 4),
        "sharpe": round(sharpe, 2),
        "max_drawdown": round(float(max_drawdown), 4),
        "calmar": round(calmar, 2),
        "daily_win_rate": round(daily_win_rate, 4),
        "turnover": round(turnover, 2),
        "total_trades": len(trades),
    }
