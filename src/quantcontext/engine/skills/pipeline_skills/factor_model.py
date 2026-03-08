"""Multi-factor scoring: value, momentum, quality, volatility."""
import pandas as pd
import numpy as np

SKILL_META = {
    "id": "factor_model",
    "type": "score",
    "params": {
        "factors": {"type": "list[str]", "description": "Factors: value, momentum, quality, volatility"},
        "weights": {"type": "list[float]", "description": "Weight per factor"},
        "top_n": {"type": "int", "description": "Keep top N scoring stocks"},
    },
    "description": "Multi-factor z-score ranking with configurable weights",
    "needs_price_enrichment": True,
}

def _z_score(series: pd.Series) -> pd.Series:
    s = series.fillna(series.median())
    std = s.std()
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    return (s - s.mean()) / std

def run(universe: pd.DataFrame, config: dict, date: str) -> pd.DataFrame:
    df = universe.copy()
    raw_weights = config.get("weights", None)

    if isinstance(raw_weights, dict) and raw_weights:
        # Dict format (documented API): {"value": 0.3, "momentum": 0.3, ...}
        factors = list(raw_weights.keys())
        weights = [float(v) for v in raw_weights.values()]
    elif isinstance(raw_weights, list) and raw_weights:
        # Legacy list format: factors must be provided separately
        factors = config.get("factors", ["value", "quality"])
        weights = [float(w) for w in raw_weights]
    else:
        factors = config.get("factors", ["value", "quality"])
        weights = [1.0 / len(factors)] * len(factors)

    top_n = config.get("top_n", 20)
    w_sum = sum(weights)
    if w_sum == 0:
        w_sum = 1.0
    weights = [w / w_sum for w in weights]
    composite = pd.Series(0.0, index=df.index)
    for factor, weight in zip(factors, weights):
        if factor == "value" and "pe_ratio" in df.columns:
            composite += -_z_score(df["pe_ratio"]) * weight
        elif factor == "momentum":
            for col in ["return_126d", "return_63d", "return_252d"]:
                if col in df.columns:
                    composite += _z_score(df[col]) * weight
                    break
        elif factor == "quality" and "roe" in df.columns:
            composite += _z_score(df["roe"]) * weight
        elif factor == "volatility" and "volatility_20d" in df.columns:
            composite += -_z_score(df["volatility_20d"]) * weight
    df["factor_score"] = composite
    df = df.sort_values("factor_score", ascending=False)
    return df.head(top_n).reset_index(drop=True)
