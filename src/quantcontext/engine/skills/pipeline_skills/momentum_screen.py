"""Screen stocks by price momentum — rank by N-day return, keep top X%."""
import math
import pandas as pd

SKILL_META = {
    "id": "momentum_screen",
    "type": "screen",
    "needs_fundamentals": False,
    "params": {
        "lookback_days": {"type": "int", "description": "Return lookback period in trading days"},
        "top_pct": {"type": "float", "description": "Keep top X% of stocks by return"},
    },
    "description": "Rank by N-day price return, keep top percentile",
    "needs_price_enrichment": True,
}

def run(universe: pd.DataFrame, config: dict, date: str) -> pd.DataFrame:
    df = universe.copy()
    lookback = config.get("lookback_days", 126)
    top_pct = config.get("top_pct", 0.2)
    return_col = f"return_{lookback}d"
    if return_col not in df.columns:
        return df
    df = df[df[return_col].notna()]
    df = df.sort_values(return_col, ascending=False)
    n_keep = max(1, math.ceil(len(df) * top_pct))
    return df.head(n_keep).reset_index(drop=True)
