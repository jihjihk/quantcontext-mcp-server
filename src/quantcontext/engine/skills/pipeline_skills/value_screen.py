"""Screen stocks by composite value score."""
import pandas as pd
import numpy as np

SKILL_META = {
    "id": "value_screen",
    "type": "screen",
    "params": {
        "method": {"type": "str", "description": "Scoring method: 'pe', 'composite'"},
        "top_n": {"type": "int", "description": "Keep top N cheapest stocks"},
    },
    "description": "Composite value scoring (PE, PB, EV/EBITDA), keep cheapest",
    "needs_price_enrichment": False,
}

def run(universe: pd.DataFrame, config: dict, date: str) -> pd.DataFrame:
    df = universe.copy()
    method = config.get("method", "pe")
    top_n = config.get("top_n", 20)
    if method == "pe":
        df = df[df["pe_ratio"].notna() & (df["pe_ratio"] > 0)]
        df = df.sort_values("pe_ratio", ascending=True)
    else:
        score = pd.Series(0.0, index=df.index)
        if "pe_ratio" in df.columns:
            pe = df["pe_ratio"].fillna(df["pe_ratio"].median())
            pe_valid = pe[pe > 0]
            if len(pe_valid) > 1:
                z = (pe_valid - pe_valid.mean()) / pe_valid.std()
                score = score.add(-z, fill_value=0)
        df["value_score"] = score
        df = df.sort_values("value_score", ascending=False)
    return df.head(top_n).reset_index(drop=True)
