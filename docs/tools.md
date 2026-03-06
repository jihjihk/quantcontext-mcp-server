# QuantContext Tool Reference

## screen_stocks

**When to use this tool:** The user wants to find stocks matching specific criteria — value stocks, momentum leaders, quality companies, or multi-factor ranked candidates. Any query about "find stocks", "screen for", "filter by", "which stocks have", or "rank stocks by" should use this tool.

**What it returns:** A ranked list of stock tickers with scores and fundamental/technical metrics. Results are capped at 30 stocks. If no stocks pass the filter, returns an empty list with a suggestion to relax criteria.

### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `universe` | `string` | `"sp500"` | Stock universe. Options: `sp500`, `russell2000`, `nasdaq100` |
| `screen_type` | `string` | `"fundamental_screen"` | Screening method (see table below) |
| `config` | `object \| null` | `null` | Screen-specific parameters. All fields optional — sensible defaults used |
| `date` | `string \| null` | `null` | Screen date (YYYY-MM-DD). Defaults to most recent trading day |

### Screen Types and Config

**`fundamental_screen`** — Filter by fundamental metrics
```json
{"pe_lt": 15, "roe_gt": 12, "debt_equity_lt": 1.0, "revenue_growth_gt": 0.05}
```

**`quality_screen`** — Profitability + balance sheet health (ROE, margins, leverage)
```json
{"roe_gt": 15, "debt_equity_lt": 0.5, "profit_margin_gt": 0.1}
```

**`momentum_screen`** — Rank by price momentum
```json
{"lookback_days": 200, "top_pct": 0.2}
```

**`value_screen`** — Cheapest by valuation
```json
{"pe_lt": 20, "top_n": 30}
```

**`factor_model`** — Multi-factor composite score
```json
{"weights": {"value": 0.3, "momentum": 0.3, "quality": 0.2, "volatility": 0.2}, "top_n": 20}
```

**`technical_signal`** — RSI and SMA signals
```json
{"rsi_period": 14, "sma_short": 50, "sma_long": 200}
```

**`mean_reversion`** — Stocks with z-score below threshold
```json
{"lookback_days": 60, "z_threshold": -1.5}
```

### Example Output

```json
{
  "screen_type": "fundamental_screen",
  "universe": "sp500",
  "date": "2024-12-31",
  "config": {"pe_lt": 15, "roe_gt": 12},
  "universe_size": 503,
  "count": 23,
  "showing": 23,
  "results": [
    {"ticker": "VTRS", "pe_ratio": 7.2, "roe": 0.18, "debt_to_equity": 0.95},
    {"ticker": "MOS", "pe_ratio": 8.1, "roe": 0.22, "debt_to_equity": 0.41},
    {"ticker": "BG", "pe_ratio": 9.4, "roe": 0.16, "debt_to_equity": 0.73}
  ]
}
```

### What to do next

- **Backtest the screen as a strategy:** Pass the same `screen_type` and `config` to `backtest_strategy` as a pipeline stage
- **Compare universes:** Run the same screen on `sp500`, `russell2000`, and `nasdaq100` to see where opportunities concentrate
- **Refine criteria:** If too many results, tighten the config. If too few, relax it

---

## backtest_strategy

**When to use this tool:** The user wants to test a trading strategy historically. Any query about "backtest", "test this strategy", "what would have happened if", "historical performance", or "how does this strategy do over time" should use this tool.

**What it returns:** Performance metrics (CAGR, Sharpe, max drawdown, Calmar, win rate, turnover), a sampled equity curve (~20 points), and a trade summary. Also includes the full equity curve for use with `factor_analysis`.

### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `stages` | `list[object]` | *required* | Pipeline stages defining the strategy (see below) |
| `universe` | `string` | `"sp500"` | Stock universe |
| `rebalance` | `string` | `"monthly"` | Rebalance frequency: `daily`, `weekly`, `monthly`, `quarterly` |
| `sizing` | `string` | `"equal_weight"` | Position sizing: `equal_weight`, `inverse_volatility` |
| `start_date` | `string` | `"2023-01-01"` | Backtest start (YYYY-MM-DD) |
| `end_date` | `string` | `"2025-12-31"` | Backtest end (YYYY-MM-DD) |
| `max_position_size` | `float \| null` | `null` | Max weight per position (0-1). E.g., 0.1 = 10% cap |
| `stop_loss` | `float \| null` | `null` | Per-position stop loss (0-1). E.g., 0.15 = sell at -15% |
| `max_drawdown` | `float \| null` | `null` | Portfolio circuit breaker (0-1). E.g., 0.2 = go to cash at -20% |

### Pipeline Stage Schema

Each stage is an object:
```json
{
  "order": 1,
  "type": "screen",
  "skill": "fundamental_screen",
  "config": {"pe_lt": 15}
}
```

- `order`: execution order (integer, ascending)
- `type`: `"screen"`, `"analyze"`, or `"signal"`
- `skill`: one of the screen types from `screen_stocks` (e.g., `fundamental_screen`, `momentum_screen`)
- `config`: same config object as `screen_stocks`

**Multi-stage example** (filter value stocks, then rank by momentum):
```json
[
  {"order": 1, "type": "screen", "skill": "fundamental_screen", "config": {"pe_lt": 15, "roe_gt": 12}},
  {"order": 2, "type": "signal", "skill": "momentum_screen", "config": {"lookback_days": 200, "top_pct": 0.3}}
]
```

### Example Output

```json
{
  "strategy": {
    "universe": "sp500",
    "rebalance": "monthly",
    "sizing": "equal_weight",
    "stages": [{"order": 1, "type": "screen", "skill": "value_screen", "config": {"pe_lt": 15}}],
    "period": "2023-01-01 to 2025-12-31"
  },
  "metrics": {
    "total_return": 0.3241,
    "cagr": 0.1012,
    "sharpe": 1.24,
    "max_drawdown": -0.1483,
    "calmar": 0.68,
    "win_rate": 0.5312,
    "turnover": 2.41,
    "total_trades": 384
  },
  "equity_curve": [
    {"date": "2023-01-03", "value": 100000.0},
    {"date": "2023-06-30", "value": 108234.5},
    {"date": "2025-12-31", "value": 132410.0}
  ],
  "equity_curve_points": 756,
  "trades": {
    "total_trades": 384,
    "buys": 204,
    "sells": 180,
    "recent_trades": [{"date": "2025-12-01", "ticker": "VTRS", "action": "BUY", "shares": 142.5, "price": 70.18}]
  },
  "full_equity_curve": ["...full array for factor_analysis..."]
}
```

### What to do next

- **Understand the returns:** Pass `full_equity_curve` to `factor_analysis` to decompose returns into market, size, value, and momentum factors
- **Compare strategies:** Run the same backtest with different screen types, rebalance frequencies, or universes
- **Add risk controls:** Set `stop_loss`, `max_position_size`, or `max_drawdown` to see how risk management affects performance

---

## factor_analysis

**When to use this tool:** The user wants to understand where returns come from — is it alpha or factor exposure? Any query about "factor analysis", "decompose returns", "where does alpha come from", "factor exposure", "Fama-French", or "what's driving the returns" should use this tool.

**What it returns:** Alpha (daily and annualized) with t-statistic, factor loadings (market, size, value, momentum) with t-statistics, R-squared, residual volatility, and interpretation hints.

### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `equity_curve` | `list[object]` | *required* | List of `{date, value}` objects. Typically from `backtest_strategy` output. Needs 30+ data points |

### Example Input

```json
{
  "equity_curve": [
    {"date": "2023-01-03", "value": 100000},
    {"date": "2023-01-04", "value": 100500},
    {"date": "2023-01-05", "value": 100234}
  ]
}
```

### Example Output

```json
{
  "alpha_daily": 0.000182,
  "alpha_annualized": 0.0469,
  "alpha_tstat": 1.87,
  "factors": {
    "Mkt-RF": {"loading": 0.8234, "tstat": 12.41},
    "SMB": {"loading": 0.2156, "tstat": 3.22},
    "HML": {"loading": 0.4891, "tstat": 5.67},
    "Mom": {"loading": -0.0812, "tstat": -1.03}
  },
  "r_squared": 0.7823,
  "residual_vol": 0.1241,
  "interpretation": {
    "alpha": "Alpha is NOT statistically significant (t-stat=1.87, need |t| >= 2)",
    "factors": "Dominant factor: HML (loading=0.4891)",
    "r_squared": "High R-squared (0.7823) — most return variance explained by known factors"
  }
}
```

### Interpreting Results

- **Alpha t-stat:** `|t| >= 2` means alpha is statistically significant at ~95% confidence. Below 2, the alpha could be noise.
- **Factor loadings:** Positive HML loading = value tilt. Positive SMB = small-cap tilt. Positive Mom = momentum tilt. The loading magnitude indicates exposure strength.
- **R-squared:** How much of the return variance is explained by the four factors. High R-squared (>0.7) means the strategy is mostly replicable with factor ETFs. Low R-squared (<0.4) means significant idiosyncratic return.
- **Residual volatility:** The annualized volatility of returns NOT explained by factors. Lower is better for factor-replication strategies.

### What to do next

- **If R-squared is high and alpha is low:** The strategy is a factor bet, not alpha. Consider whether you can get the same exposure cheaper with factor ETFs
- **If alpha is significant:** The strategy has genuine edge beyond factor exposure. Consider increasing allocation
- **Compare factor exposures:** Run factor_analysis on different strategies to see which has the most differentiated return source
