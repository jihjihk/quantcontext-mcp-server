"""Screen stocks by fundamental thresholds."""
import pandas as pd

SKILL_META = {
    "id": "fundamental_screen",
    "type": "screen",
    "params": {
        "pe_lt": {"type": "float", "description": "Max trailing PE ratio"},
        "pe_gt": {"type": "float", "description": "Min trailing PE ratio"},
        "roe_gt": {"type": "float", "description": "Min return on equity (decimal, e.g. 0.15 = 15%)"},
        "debt_equity_lt": {"type": "float", "description": "Max debt-to-equity ratio"},
        "rev_growth_gt": {"type": "float", "description": "Min revenue growth (decimal)"},
    },
    "description": "Filter stocks by fundamental thresholds (PE, ROE, D/E, revenue growth)",
    "needs_price_enrichment": False,
}


def run(universe: pd.DataFrame, config: dict, date: str) -> pd.DataFrame:
    df = universe.copy()
    if "pe_lt" in config and config["pe_lt"] is not None:
        df = df[df["pe_ratio"].notna() & (df["pe_ratio"] < config["pe_lt"])]
    if "pe_gt" in config and config["pe_gt"] is not None:
        df = df[df["pe_ratio"].notna() & (df["pe_ratio"] > config["pe_gt"])]
    if "roe_gt" in config and config["roe_gt"] is not None:
        df = df[df["roe"].notna() & (df["roe"] > config["roe_gt"])]
    if "debt_equity_lt" in config and config["debt_equity_lt"] is not None:
        df = df[df["debt_to_equity"].notna() & (df["debt_to_equity"] < config["debt_equity_lt"])]
    if "rev_growth_gt" in config and config["rev_growth_gt"] is not None:
        df = df[df["revenue_growth"].notna() & (df["revenue_growth"] > config["rev_growth_gt"])]
    return df.reset_index(drop=True)
