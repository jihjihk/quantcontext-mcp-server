from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
FINANCIALS_DIR = CACHE_DIR / "financials"
FINANCIALS_DIR.mkdir(exist_ok=True)

PRICES_CACHE_PATH = CACHE_DIR / "prices.parquet"
PRICES_CSV_FALLBACK_PATH = CACHE_DIR / "prices.csv"
FACTORS_CACHE_PATH = CACHE_DIR / "ff_factors.parquet"
FACTORS_CSV_FALLBACK = CACHE_DIR / "ff_factors.csv"
SP500_CACHE_PATH = CACHE_DIR / "sp500_tickers.json"
REMOTE_CACHE_BASE_URL = os.getenv("MARKET_DATA_BASE_URL", "").rstrip("/")

FALLBACK_SP500_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "LLY", "AVGO", "TSLA",
    "JPM", "V", "UNH", "XOM", "MA", "COST", "PG", "HD", "JNJ", "ABBV",
    "WMT", "BAC", "CRM", "KO", "ORCL", "MRK", "CVX", "AMD", "PEP", "TMO",
    "ADBE", "CSCO", "ACN", "MCD", "NFLX", "ABT", "LIN", "DHR", "INTU", "WFC",
    "QCOM", "TXN", "PM", "AMGN", "CAT", "DIS", "VZ", "IBM", "GS", "NOW",
    "SPGI", "GE", "RTX", "PFE", "ISRG", "HON", "LOW", "T", "BKNG", "BLK",
    "AXP", "UNP", "MS", "AMAT", "SYK", "NEE", "PLD", "C", "SBUX", "MDT",
    "ADP", "DE", "TJX", "VRTX", "ELV", "GILD", "MMC", "LRCX", "SO", "NKE",
    "MU", "SCHW", "BA", "PGR", "COP", "PANW", "ADI", "ETN", "MDLZ", "TMUS",
]

FALLBACK_NASDAQ100_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "AVGO", "TSLA", "COST", "NFLX",
    "AMD", "ADBE", "CSCO", "INTU", "QCOM", "TXN", "AMGN", "ISRG", "BKNG", "AMAT",
    "LRCX", "MU", "PANW", "ADI", "MDLZ", "TMUS", "ADP", "GILD", "VRTX", "REGN",
    "SNPS", "CDNS", "KLAC", "MRVL", "FTNT", "ABNB", "TEAM", "DXCM", "ILMN", "BIIB",
    "ZS", "CRWD", "WDAY", "MNST", "ODFL", "CSGP", "ANSS", "CPRT", "PCAR", "ON",
]

FALLBACK_RUSSELL2000_TICKERS = [
    "SMCI", "CRUS", "CARG", "LUMN", "IRBT", "SONO", "CHGG", "BGFV", "PRTS", "RGS",
    "BLMN", "CAKE", "DINE", "JACK", "BJRI", "PLAY", "DIN", "TXRH", "EAT", "RUTH",
    "SHAK", "WING", "LOCO", "TAST", "NDLS", "ARCO", "FRGI", "PTLO", "KRUS", "BROS",
    "CAVA", "SG", "RVLV", "BOOT", "DBI", "SCVL", "GCO", "CAL", "CRI", "OXM",
    "GIII", "LEVI", "HBI", "PVH", "URBN", "ANF", "AEO", "EXPR", "TLYS", "ZUMZ",
]


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.index = pd.to_datetime(out.index).tz_localize(None)
    out = out.sort_index()
    return out


def _filter_prices(df: pd.DataFrame, tickers: list[str], start: str, end: str) -> pd.DataFrame:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    in_range = (df.index >= start_ts) & (df.index <= end_ts)
    cols = [t for t in tickers if t in df.columns]
    if not cols:
        return pd.DataFrame(index=df.index[in_range])
    return df.loc[in_range, cols]


def _try_download_remote_cache(rel_path: str, cache_path: Path) -> bool:
    if not REMOTE_CACHE_BASE_URL:
        return False

    remote_url = f"{REMOTE_CACHE_BASE_URL}/{rel_path}"
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(remote_url, timeout=20) as response:
            cache_path.write_bytes(response.read())
        return True
    except Exception:
        return False


def _read_cached_prices() -> pd.DataFrame | None:
    if PRICES_CACHE_PATH.exists():
        try:
            return _normalize_index(pd.read_parquet(PRICES_CACHE_PATH))
        except Exception:
            # Keep runtime resilient when parquet optional deps are missing.
            pass

    if PRICES_CSV_FALLBACK_PATH.exists():
        try:
            df = pd.read_csv(PRICES_CSV_FALLBACK_PATH, index_col=0, parse_dates=True)
            return _normalize_index(df)
        except Exception:
            return None

    return None


def _write_cached_prices(df: pd.DataFrame) -> None:
    try:
        df.to_parquet(PRICES_CACHE_PATH)
        return
    except Exception:
        # Fallback cache format if parquet engine is unavailable in runtime.
        pass

    try:
        df.to_csv(PRICES_CSV_FALLBACK_PATH)
    except Exception:
        # Cache write failure should not block the backtest path.
        return


def _download_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    data = yf.download(tickers, start=start, end=end, progress=False, group_by="column")
    if data.empty:
        raise RuntimeError("No price data returned from yfinance")

    if isinstance(data.columns, pd.MultiIndex):
        if "Close" not in data.columns.get_level_values(0):
            raise RuntimeError("Price payload missing Close data")
        prices = data["Close"]
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=tickers[0])
    else:
        if "Close" not in data.columns:
            raise RuntimeError("Price payload missing Close column")
        if len(tickers) == 1:
            prices = data[["Close"]].rename(columns={"Close": tickers[0]})
        else:
            # Multi-ticker downloads should be MultiIndex; if not, fail clearly.
            raise RuntimeError("Unexpected yfinance payload format for multi-ticker request")

    prices = _normalize_index(prices)
    return prices


def fetch_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Fetch daily close prices using shared cache file at engine/.cache/prices.parquet."""
    unique_tickers = sorted(set(tickers))

    if not PRICES_CACHE_PATH.exists() and not PRICES_CSV_FALLBACK_PATH.exists():
        _try_download_remote_cache("prices.parquet", PRICES_CACHE_PATH)
        if not PRICES_CACHE_PATH.exists():
            _try_download_remote_cache("prices.csv", PRICES_CSV_FALLBACK_PATH)

    cached = _read_cached_prices()
    if cached is not None:
        cached_slice = _filter_prices(cached, unique_tickers, start, end)
        has_all = all(t in cached_slice.columns for t in unique_tickers)
        has_values = has_all and all(not cached_slice[t].dropna().empty for t in unique_tickers)
        if has_values and not cached_slice.empty:
            return cached_slice

    try:
        live = _download_prices(unique_tickers, start, end)
    except Exception as exc:
        if cached is not None:
            fallback = _filter_prices(cached, unique_tickers, start, end)
            if not fallback.empty:
                return fallback
        raise RuntimeError(f"Failed to fetch prices: {exc}") from exc

    merged = live
    if cached is not None:
        merged = live.combine_first(cached)
    merged = _normalize_index(merged)
    _write_cached_prices(merged)

    result = _filter_prices(merged, unique_tickers, start, end)
    if result.empty:
        raise RuntimeError("No prices available after cache/live fetch")
    return result


def fetch_sp500_tickers() -> list[str]:
    """Return current S&P 500 tickers. Cache result."""
    if not SP500_CACHE_PATH.exists():
        _try_download_remote_cache("sp500_tickers.json", SP500_CACHE_PATH)

    if SP500_CACHE_PATH.exists():
        with open(SP500_CACHE_PATH) as f:
            return json.load(f)

    try:
        table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers = table["Symbol"].str.replace(".", "-", regex=False).tolist()
    except Exception:
        tickers = FALLBACK_SP500_TICKERS

    with open(SP500_CACHE_PATH, "w") as f:
        json.dump(tickers, f)
    return tickers


NASDAQ100_CACHE_PATH = CACHE_DIR / "nasdaq100_tickers.json"


def fetch_nasdaq100_tickers() -> list[str]:
    """Return current Nasdaq-100 tickers. Cache result."""
    if not NASDAQ100_CACHE_PATH.exists():
        _try_download_remote_cache("nasdaq100_tickers.json", NASDAQ100_CACHE_PATH)

    if NASDAQ100_CACHE_PATH.exists():
        with open(NASDAQ100_CACHE_PATH) as f:
            return json.load(f)

    try:
        table = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[4]
        tickers = table["Ticker"].str.replace(".", "-", regex=False).tolist()
    except Exception:
        tickers = FALLBACK_NASDAQ100_TICKERS

    with open(NASDAQ100_CACHE_PATH, "w") as f:
        json.dump(tickers, f)
    return tickers


def fetch_russell2000_tickers() -> list[str]:
    """Return representative Russell 2000 tickers (fallback list only)."""
    return list(FALLBACK_RUSSELL2000_TICKERS)


def fetch_financials(ticker: str) -> dict:
    """Fetch basic financials and cache by ticker at engine/.cache/financials/{ticker}.json."""
    cache_path = FINANCIALS_DIR / f"{ticker}.json"
    if not cache_path.exists():
        _try_download_remote_cache(f"financials/{ticker}.json", cache_path)

    if cache_path.exists() and (time.time() - cache_path.stat().st_mtime < 86400):
        with open(cache_path) as f:
            return json.load(f)

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch financials for {ticker}: {exc}") from exc

    result = {
        "ticker": ticker,
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "revenue": info.get("totalRevenue"),
        "revenue_growth": info.get("revenueGrowth"),
        "roe": info.get("returnOnEquity"),
        "debt_to_equity": info.get("debtToEquity"),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector"),
        "name": info.get("shortName"),
    }

    with open(cache_path, "w") as f:
        json.dump(result, f)
    return result


def enrich_with_price_data(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """Enrich a universe DataFrame with price-derived columns.

    Downloads ~300 days of price history ending at *date* for each ticker
    in *df* and computes momentum, volatility, and technical indicators.
    """
    import numpy as np

    if "ticker" not in df.columns or df.empty:
        return df

    tickers = df["ticker"].tolist()
    end_ts = pd.Timestamp(date)
    start_ts = end_ts - pd.Timedelta(days=420)  # ~300 trading days buffer

    try:
        prices = fetch_prices(tickers, start_ts.strftime("%Y-%m-%d"), date)
    except Exception:
        return df

    # Build a dict of ticker -> computed values
    records: dict[str, dict] = {}
    for ticker in tickers:
        rec: dict = {}
        if ticker not in prices.columns:
            records[ticker] = rec
            continue

        series = prices[ticker].dropna()
        if len(series) < 30:
            records[ticker] = rec
            continue

        last_price = float(series.iloc[-1])

        # N-day total returns
        for n, col in [(21, "return_21d"), (63, "return_63d"),
                        (126, "return_126d"), (252, "return_252d")]:
            if len(series) > n:
                rec[col] = float(series.iloc[-1] / series.iloc[-n] - 1)

        # 20-day annualized volatility
        if len(series) > 21:
            daily_ret = series.pct_change().dropna().iloc[-20:]
            rec["volatility_20d"] = float(daily_ret.std() * np.sqrt(252))

        # RSI 14
        if len(series) > 15:
            delta = series.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            last_rsi = rsi.iloc[-1]
            if pd.notna(last_rsi):
                rec["rsi_14"] = float(last_rsi)

        # SMA 50, SMA 200
        if len(series) >= 50:
            rec["sma_50"] = float(series.rolling(50).mean().iloc[-1])
        if len(series) >= 200:
            rec["sma_200"] = float(series.rolling(200).mean().iloc[-1])

        # Bollinger band position (20-day)
        if len(series) >= 20:
            sma20 = series.rolling(20).mean()
            std20 = series.rolling(20).std()
            bb_width = 4 * std20
            bb_pos = (series - (sma20 - 2 * std20)) / bb_width
            last_bb = bb_pos.iloc[-1]
            if pd.notna(last_bb):
                rec["bb_position"] = float(last_bb)

        # Z-score 60d
        if len(series) >= 60:
            rolling_mean = series.rolling(60).mean()
            rolling_std = series.rolling(60).std()
            last_std = rolling_std.iloc[-1]
            if pd.notna(last_std) and last_std > 0:
                rec["z_score_60d"] = float(
                    (last_price - rolling_mean.iloc[-1]) / last_std
                )

        records[ticker] = rec

    # Merge computed columns into df
    enrichment = pd.DataFrame.from_dict(records, orient="index")
    if enrichment.empty:
        return df

    df = df.set_index("ticker")
    for col in enrichment.columns:
        df[col] = enrichment[col]
    df = df.reset_index()

    return df


def get_universe(date: str, universe: str = "sp500") -> pd.DataFrame:
    """Return a DataFrame of all tickers in the universe with fundamentals.

    Columns: ticker, pe_ratio, forward_pe, roe, debt_to_equity,
             revenue_growth, market_cap, sector, name
    """
    if universe == "sp500":
        tickers = fetch_sp500_tickers()
    elif universe == "nasdaq100":
        tickers = fetch_nasdaq100_tickers()
    elif universe == "russell2000":
        tickers = fetch_russell2000_tickers()
    else:
        tickers = FALLBACK_SP500_TICKERS[:90]

    rows = []
    for ticker in tickers:
        try:
            fin = fetch_financials(ticker)
            rows.append(fin)
        except Exception:
            continue

    df = pd.DataFrame(rows)
    df = enrich_with_price_data(df, date)
    return df


def _download_french_factors() -> pd.DataFrame:
    """Download Fama-French 3-factor + Momentum daily data from Ken French's site."""
    import io as _io
    from zipfile import ZipFile
    from urllib.request import urlopen

    # 3 factors
    ff3_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    with urlopen(ff3_url, timeout=30) as resp:
        zf = ZipFile(_io.BytesIO(resp.read()))
        csv_name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
        raw = zf.read(csv_name).decode("utf-8")

    lines = raw.strip().split("\n")
    data_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and stripped[0].isdigit() and len(stripped.split(",")[0].strip()) == 8:
            data_start = i
            break
    if data_start is None:
        raise RuntimeError("Could not parse French factor data")

    data_lines = []
    for line in lines[data_start:]:
        parts = line.strip().split(",")
        if len(parts) >= 4 and parts[0].strip().isdigit() and len(parts[0].strip()) == 8:
            data_lines.append(line)
        elif len(parts) < 4 or not parts[0].strip():
            break

    header = "Date,Mkt-RF,SMB,HML,RF\n"
    csv_str = header + "\n".join(data_lines)
    df = pd.read_csv(_io.StringIO(csv_str))
    df["Date"] = pd.to_datetime(df["Date"].astype(str).str.strip(), format="%Y%m%d")
    df = df.set_index("Date")
    for col in ["Mkt-RF", "SMB", "HML", "RF"]:
        df[col] = df[col].astype(float) / 100.0

    # Momentum factor
    try:
        mom_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip"
        with urlopen(mom_url, timeout=30) as resp:
            zf = ZipFile(_io.BytesIO(resp.read()))
            csv_name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
            raw = zf.read(csv_name).decode("utf-8")

        lines = raw.strip().split("\n")
        data_start = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and len(stripped.split(",")[0].strip()) == 8:
                data_start = i
                break

        data_lines = []
        if data_start is not None:
            for line in lines[data_start:]:
                parts = line.strip().split(",")
                if len(parts) >= 2 and parts[0].strip().isdigit() and len(parts[0].strip()) == 8:
                    data_lines.append(line)
                elif not parts[0].strip():
                    break

        mom_csv = "Date,Mom\n" + "\n".join(data_lines)
        mom_df = pd.read_csv(_io.StringIO(mom_csv))
        mom_df["Date"] = pd.to_datetime(mom_df["Date"].astype(str).str.strip(), format="%Y%m%d")
        mom_df = mom_df.set_index("Date")
        mom_df["Mom"] = mom_df["Mom"].astype(float) / 100.0
        df = df.join(mom_df, how="left")
        df["Mom"] = df["Mom"].fillna(0.0)
    except Exception:
        df["Mom"] = 0.0

    return df


def get_factors(start: str, end: str) -> pd.DataFrame:
    """Return daily Fama-French factor returns (Mkt-RF, SMB, HML, Mom, RF)."""
    for cache_path, csv_path in [(FACTORS_CACHE_PATH, FACTORS_CSV_FALLBACK)]:
        if cache_path.exists():
            try:
                df = pd.read_parquet(cache_path)
                df.index = pd.to_datetime(df.index).tz_localize(None)
                mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
                if mask.any():
                    return df.loc[mask]
            except Exception:
                pass
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
                if mask.any():
                    return df.loc[mask]
            except Exception:
                pass

    df = _download_french_factors()
    try:
        df.to_parquet(FACTORS_CACHE_PATH)
    except Exception:
        df.to_csv(FACTORS_CSV_FALLBACK)

    mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
    return df.loc[mask]
