"""pytest configuration: replace all external API calls with synthetic sample data.

No yfinance calls, no Wikipedia scrapes, no Ken French factor downloads.
Tests run fully offline in seconds.
"""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

# ── Fixed universe ─────────────────────────────────────────────────────────────
_SP500 = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "UNH",
    "XOM", "CVX", "JNJ", "PG", "KO", "PEP", "WMT", "HD", "MA", "ABBV",
]
_NASDAQ100 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "NFLX",
    "AMD", "ADBE", "CSCO", "INTU", "QCOM",
]

_START = "2023-01-01"
_END   = "2024-12-31"

# ── Synthetic price data ───────────────────────────────────────────────────────

def _build_prices() -> pd.DataFrame:
    rng    = np.random.default_rng(42)
    dates  = pd.bdate_range(_START, _END)
    tickers = sorted(set(_SP500 + _NASDAQ100))
    n      = len(dates)
    data   = {}
    for i, ticker in enumerate(tickers):
        # Varied drift so momentum/value screens actually differentiate stocks
        drift = 0.0004 * ((i % 7) - 3)   # −0.0012 .. +0.0016
        vol   = 0.012 + 0.004 * (i % 4)
        rets  = rng.normal(drift, vol, size=n)
        data[ticker] = 100.0 * np.exp(np.cumsum(rets))
    return pd.DataFrame(data, index=dates)


_PRICES = _build_prices()


def _fetch_prices(tickers, start, end):
    cols = [t for t in tickers if t in _PRICES.columns]
    mask = (_PRICES.index >= pd.Timestamp(start)) & (_PRICES.index <= pd.Timestamp(end))
    return _PRICES.loc[mask, cols].copy() if cols else pd.DataFrame(index=_PRICES.index[mask])


# ── Synthetic universe ─────────────────────────────────────────────────────────

def _universe_row(ticker: str, date: str) -> dict:
    """One row with every column any screen skill may need."""
    h   = abs(hash(ticker)) % 100
    end_ts   = pd.Timestamp(date)
    start_ts = end_ts - pd.Timedelta(days=420)

    rec: dict = {"ticker": ticker}

    if ticker in _PRICES.columns:
        series = _PRICES.loc[
            (_PRICES.index >= start_ts) & (_PRICES.index <= end_ts), ticker
        ].dropna()

        if len(series) >= 2:
            for n, col in [(21, "return_21d"), (63, "return_63d"),
                           (126, "return_126d"), (252, "return_252d")]:
                if len(series) > n:
                    rec[col] = float(series.iloc[-1] / series.iloc[-n] - 1)

            if len(series) > 21:
                rec["volatility_20d"] = float(
                    series.pct_change().dropna().iloc[-20:].std() * np.sqrt(252)
                )

            if len(series) >= 50:
                rec["sma_50"] = float(series.rolling(50).mean().iloc[-1])
            if len(series) >= 200:
                rec["sma_200"] = float(series.rolling(200).mean().iloc[-1])

            if len(series) > 15:
                delta = series.diff()
                gain  = delta.where(delta > 0, 0).rolling(14).mean()
                loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi_val = (100 - 100 / (1 + gain / loss)).iloc[-1]
                if pd.notna(rsi_val):
                    rec["rsi_14"] = float(rsi_val)

            if len(series) >= 20:
                sma20 = series.rolling(20).mean()
                std20 = series.rolling(20).std()
                bb_pos = (series - (sma20 - 2 * std20)) / (4 * std20)
                last_bb = bb_pos.iloc[-1]
                if pd.notna(last_bb):
                    rec["bb_position"] = float(last_bb)

            if len(series) >= 60:
                rm  = series.rolling(60).mean()
                rs2 = series.rolling(60).std()
                last_std = rs2.iloc[-1]
                if pd.notna(last_std) and last_std > 0:
                    rec["z_score_60d"] = float(
                        (series.iloc[-1] - rm.iloc[-1]) / last_std
                    )

    # Fundamental fields — varied so PE/ROE screens actually filter
    rec["pe_ratio"]       = 10.0 + h * 0.5        # 10 .. 60
    rec["forward_pe"]     = 9.0  + h * 0.4
    rec["revenue"]        = 1e9  * (1 + h)
    rec["revenue_growth"] = 0.05 + 0.01 * (h % 10)
    rec["roe"]            = 0.05 + 0.01 * (h % 20)  # 5% .. 25%
    rec["debt_to_equity"] = 0.1  + 0.05 * (h % 10)
    rec["market_cap"]     = 1e10 * (1 + h % 10)
    rec["sector"]         = ["Technology", "Financials", "Healthcare"][h % 3]
    rec["name"]           = ticker
    return rec


def _get_universe(date: str, universe: str = "sp500", fundamentals: bool = True, *, enrich: bool = True, prices: pd.DataFrame | None = None) -> pd.DataFrame:
    tickers = _SP500 if universe != "nasdaq100" else _NASDAQ100
    return pd.DataFrame([_universe_row(t, date) for t in tickers])


# ── Synthetic Fama-French factors ──────────────────────────────────────────────

def _build_factors() -> pd.DataFrame:
    rng   = np.random.default_rng(99)
    dates = pd.bdate_range(_START, _END)
    n     = len(dates)
    return pd.DataFrame({
        "Mkt-RF": rng.normal(0.0003, 0.010, n),
        "SMB":    rng.normal(0.0001, 0.005, n),
        "HML":    rng.normal(0.0001, 0.005, n),
        "Mom":    rng.normal(0.0002, 0.006, n),
        "RF":     np.full(n, 0.00018),
    }, index=dates)


_FACTORS = _build_factors()


def _get_factors(start: str, end: str) -> pd.DataFrame:
    mask = (_FACTORS.index >= pd.Timestamp(start)) & (_FACTORS.index <= pd.Timestamp(end))
    return _FACTORS.loc[mask].copy()


# ── Autouse fixture ────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_data_layer():
    """Patch every external data call. Active for all tests automatically."""
    with (
        patch("quantcontext.engine.backtest_engine.fetch_prices", side_effect=_fetch_prices),
        patch("quantcontext.engine.pipeline_executor.get_universe", side_effect=_get_universe),
        patch("quantcontext.engine.factor_analysis.get_factors", side_effect=_get_factors),
    ):
        yield
