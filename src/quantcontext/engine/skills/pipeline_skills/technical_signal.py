"""Technical analysis signals: RSI, SMA crossover, Bollinger bands."""
import pandas as pd
import numpy as np

SKILL_META = {
    "id": "technical_signal",
    "type": "signal",
    "needs_fundamentals": False,
    "params": {
        "indicators": {"type": "list[str]", "description": "Indicators: RSI, SMA_cross, bollinger"},
        "rsi_oversold": {"type": "float", "description": "RSI oversold threshold (default 30)"},
        "rsi_overbought": {"type": "float", "description": "RSI overbought threshold (default 70)"},
    },
    "description": "Score stocks by technical indicators",
    "needs_price_enrichment": True,
}

def run(universe: pd.DataFrame, config: dict, date: str) -> pd.DataFrame:
    df = universe.copy()
    indicators = config.get("indicators", ["RSI"])
    score = pd.Series(0.0, index=df.index)
    if "RSI" in indicators and "rsi_14" in df.columns:
        oversold = config.get("rsi_oversold", 30)
        overbought = config.get("rsi_overbought", 70)
        rsi = df["rsi_14"].fillna(50)
        score += np.where(rsi < oversold, 1.0, np.where(rsi > overbought, -1.0, 0.0))
    if "SMA_cross" in indicators and "sma_50" in df.columns and "sma_200" in df.columns:
        bullish = (df["sma_50"] > df["sma_200"]).astype(float)
        score += bullish
    if "bollinger" in indicators and "bb_position" in df.columns:
        bb = df["bb_position"].fillna(0.5)
        score += np.where(bb < 0.2, 1.0, np.where(bb > 0.8, -1.0, 0.0))
    df["signal_score"] = score
    return df
