"""Mean reversion: buy oversold stocks based on z-score from rolling mean."""
import pandas as pd

SKILL_META = {
    "id": "mean_reversion",
    "type": "screen",
    "needs_fundamentals": False,
    "params": {
        "z_threshold": {"type": "float", "description": "Buy when z-score below this"},
        "lookback": {"type": "int", "description": "Rolling window in days"},
    },
    "description": "Z-score from rolling mean, buy below threshold",
    "needs_price_enrichment": True,
}

def run(universe: pd.DataFrame, config: dict, date: str) -> pd.DataFrame:
    df = universe.copy()
    z_threshold = config.get("z_threshold", -2.0)
    z_col = None
    for col in df.columns:
        if "z_score" in col:
            z_col = col
            break
    if z_col is None:
        return df
    df = df[df[z_col].notna() & (df[z_col] < z_threshold)]
    return df.reset_index(drop=True)
