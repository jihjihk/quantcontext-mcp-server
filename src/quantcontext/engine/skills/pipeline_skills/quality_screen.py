"""Screen stocks by quality metrics."""
import pandas as pd

SKILL_META = {
    "id": "quality_screen",
    "type": "screen",
    "params": {
        "roe_gt": {"type": "float", "description": "Min return on equity"},
        "debt_equity_lt": {"type": "float", "description": "Max debt-to-equity"},
        "margin_gt": {"type": "float", "description": "Min profit margin"},
    },
    "description": "Filter by quality metrics (ROE, debt, margins)",
    "needs_price_enrichment": False,
}

def run(universe: pd.DataFrame, config: dict, date: str) -> pd.DataFrame:
    df = universe.copy()
    if "roe_gt" in config and config["roe_gt"] is not None:
        df = df[df["roe"].notna() & (df["roe"] > config["roe_gt"])]
    if "debt_equity_lt" in config and config["debt_equity_lt"] is not None:
        df = df[df["debt_to_equity"].notna() & (df["debt_to_equity"] < config["debt_equity_lt"])]
    if "margin_gt" in config and config["margin_gt"] is not None and "profit_margin" in df.columns:
        df = df[df["profit_margin"].notna() & (df["profit_margin"] > config["margin_gt"])]
    return df.reset_index(drop=True)
