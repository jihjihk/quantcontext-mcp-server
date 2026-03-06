# QuantContext Example Workflows

Three complete examples showing how an AI agent uses QuantContext tools. Each example shows the user prompt, the tool call the agent makes, and how the agent interprets the results.

---

## Example 1: Find Value Stocks (Single Tool)

**User:** "Find S&P 500 stocks trading below 12x earnings with return on equity above 15%"

**Agent reasoning:** The user wants to filter stocks by fundamental criteria (PE and ROE). This maps to `screen_stocks` with `fundamental_screen`.

**Agent calls `screen_stocks`:**
```json
{
  "universe": "sp500",
  "screen_type": "fundamental_screen",
  "config": {
    "pe_lt": 12,
    "roe_gt": 15
  }
}
```

**Tool returns** (illustrative, from a screen run on 2025-03-05 — your results will differ)**:**
```json
{
  "screen_type": "fundamental_screen",
  "universe": "sp500",
  "date": "2025-03-05",
  "config": {"pe_lt": 12, "roe_gt": 15},
  "universe_size": 503,
  "count": 14,
  "showing": 14,
  "results": [
    {"ticker": "VTRS", "pe_ratio": 7.2, "roe": 0.183, "debt_to_equity": 0.95, "revenue_growth": 0.04},
    {"ticker": "MOS", "pe_ratio": 8.1, "roe": 0.221, "debt_to_equity": 0.41, "revenue_growth": 0.11},
    {"ticker": "BG", "pe_ratio": 9.4, "roe": 0.162, "debt_to_equity": 0.73, "revenue_growth": 0.03},
    {"ticker": "ABBV", "pe_ratio": 10.8, "roe": 0.472, "debt_to_equity": 5.73, "revenue_growth": 0.05},
    {"ticker": "CI", "pe_ratio": 11.2, "roe": 0.157, "debt_to_equity": 0.72, "revenue_growth": 0.08}
  ]
}
```

**Agent responds:** "I found 14 S&P 500 stocks trading below 12x earnings with ROE above 15%. The standout is VTRS (Viatris) at just 7.2x PE with 18.3% ROE. Two things to note:

1. ABBV has exceptional ROE (47.2%) but very high leverage (5.73x debt/equity) — the high ROE is partly a function of a small equity base.
2. MOS looks interesting: low PE (8.1x), strong ROE (22.1%), conservative leverage (0.41x), and double-digit revenue growth (11%).

Want me to backtest a strategy that buys these value stocks?"

---

## Example 2: Build and Test a Momentum Strategy (Two Tools)

**User:** "I want to test a strategy that buys the top 20% momentum stocks in the Nasdaq 100, rebalanced monthly. How would it have done over the last 2 years?"

**Agent reasoning:** This is a backtest request. I need `backtest_strategy` with a `momentum_screen` stage. The user wants 2 years of history with monthly rebalance.

**Agent calls `backtest_strategy`:**
```json
{
  "stages": [
    {
      "order": 1,
      "type": "screen",
      "skill": "momentum_screen",
      "config": {"lookback_days": 200, "top_pct": 0.2}
    }
  ],
  "universe": "nasdaq100",
  "rebalance": "monthly",
  "sizing": "equal_weight",
  "start_date": "2023-03-01",
  "end_date": "2025-03-01"
}
```

**Tool returns:**
```json
{
  "strategy": {
    "universe": "nasdaq100",
    "rebalance": "monthly",
    "sizing": "equal_weight",
    "stages": [{"order": 1, "type": "screen", "skill": "momentum_screen", "config": {"lookback_days": 200, "top_pct": 0.2}}],
    "period": "2023-03-01 to 2025-03-01"
  },
  "metrics": {
    "total_return": 0.4812,
    "cagr": 0.2187,
    "sharpe": 1.56,
    "max_drawdown": -0.1234,
    "calmar": 1.77,
    "win_rate": 0.5523,
    "turnover": 3.82,
    "total_trades": 412
  },
  "equity_curve_points": 504,
  "full_equity_curve": [{"date": "2023-03-01", "value": 100000}, "..."]
}
```

**Agent responds:** "The top-20% momentum strategy on Nasdaq 100 performed well over the last 2 years:

- **Total return:** +48.1% (21.9% CAGR)
- **Sharpe ratio:** 1.56 — strong risk-adjusted returns
- **Max drawdown:** -12.3% — manageable
- **Win rate:** 55.2% of trading days positive
- **Turnover:** 3.82x annually — fairly active, with 412 total trades

The Calmar ratio (CAGR / max drawdown) of 1.77 suggests good return per unit of peak-to-trough risk. The high turnover is expected for a momentum strategy.

Want me to decompose these returns to understand the factor exposures?"

**User:** "Yes, where is the return coming from?"

**Agent calls `factor_analysis`:**
```json
{
  "equity_curve": [{"date": "2023-03-01", "value": 100000}, "...504 points..."]
}
```

**Tool returns:**
```json
{
  "alpha_daily": 0.000312,
  "alpha_annualized": 0.0821,
  "alpha_tstat": 2.34,
  "factors": {
    "Mkt-RF": {"loading": 1.1234, "tstat": 18.92},
    "SMB": {"loading": -0.3456, "tstat": -4.12},
    "HML": {"loading": -0.2891, "tstat": -3.45},
    "Mom": {"loading": 0.4523, "tstat": 6.78}
  },
  "r_squared": 0.8234,
  "residual_vol": 0.0912,
  "interpretation": {
    "alpha": "Alpha is statistically significant (t-stat=2.34)",
    "factors": "Dominant factor: Mkt-RF (loading=1.1234)",
    "r_squared": "High R-squared (0.8234) — most return variance explained by known factors"
  }
}
```

**Agent responds:** "Factor decomposition reveals an interesting picture:

**Alpha is statistically significant** (8.2% annualized, t-stat 2.34) — there is genuine edge beyond factor exposure.

**Factor exposures:**
- **Market (Mkt-RF):** 1.12 loading — the strategy runs with slightly higher beta than the market, amplifying both gains and losses
- **Size (SMB):** -0.35 loading — tilted toward large caps (expected for Nasdaq 100)
- **Value (HML):** -0.29 loading — anti-value, which makes sense for a momentum strategy that favors expensive, fast-growing stocks
- **Momentum (Mom):** 0.45 loading — significant momentum exposure (as expected)

**R-squared: 0.82** — 82% of return variance is explained by these four factors. The remaining 18% is idiosyncratic.

**Key insight:** Despite the high R-squared, the strategy generates significant alpha. The momentum factor alone (0.45 loading) doesn't fully explain the returns — the stock selection within the momentum bucket is adding value. However, the 1.12 market beta means this strategy will significantly underperform in a bear market."

---

## Example 3: Full Strategy Research (Three Tools)

**User:** "I want to build a value-momentum strategy. Screen for cheap stocks, rank by momentum, backtest it, and tell me if the alpha is real."

**Agent reasoning:** This is a full research workflow. I need to:
1. Screen for value stocks (to understand the universe)
2. Backtest a two-stage pipeline (value filter + momentum rank)
3. Run factor analysis on the backtest

**Step 1 — Agent calls `screen_stocks` to preview the universe:**
```json
{
  "universe": "sp500",
  "screen_type": "fundamental_screen",
  "config": {"pe_lt": 15, "roe_gt": 10}
}
```

**Tool returns:** 28 stocks pass the screen.

**Agent:** "Found 28 S&P 500 stocks with PE below 15 and ROE above 10%. Now I'll backtest a strategy that applies this value filter, then ranks the survivors by 200-day momentum and picks the top 30%."

**Step 2 — Agent calls `backtest_strategy`:**
```json
{
  "stages": [
    {"order": 1, "type": "screen", "skill": "fundamental_screen", "config": {"pe_lt": 15, "roe_gt": 10}},
    {"order": 2, "type": "signal", "skill": "momentum_screen", "config": {"lookback_days": 200, "top_pct": 0.3}}
  ],
  "universe": "sp500",
  "rebalance": "monthly",
  "sizing": "equal_weight",
  "start_date": "2022-01-01",
  "end_date": "2025-01-01",
  "max_position_size": 0.15,
  "stop_loss": 0.15
}
```

**Tool returns:**
```json
{
  "metrics": {
    "total_return": 0.4123,
    "cagr": 0.1216,
    "sharpe": 1.31,
    "max_drawdown": -0.1567,
    "calmar": 0.78,
    "win_rate": 0.5234,
    "turnover": 2.12,
    "total_trades": 256
  }
}
```

**Step 3 — Agent calls `factor_analysis` on the equity curve:**
```json
{
  "equity_curve": ["...from backtest full_equity_curve..."]
}
```

**Tool returns:**
```json
{
  "alpha_annualized": 0.0534,
  "alpha_tstat": 1.92,
  "factors": {
    "Mkt-RF": {"loading": 0.7812, "tstat": 14.23},
    "SMB": {"loading": 0.1234, "tstat": 1.89},
    "HML": {"loading": 0.5678, "tstat": 7.34},
    "Mom": {"loading": 0.2345, "tstat": 3.45}
  },
  "r_squared": 0.7456
}
```

**Agent responds:** "Here's your value-momentum strategy analysis:

**Performance (3 years, 2022-2025):**
- Total return: +41.2% (12.2% CAGR)
- Sharpe: 1.31 — solid risk-adjusted returns
- Max drawdown: -15.7% — contained by the 15% stop-loss
- The strategy held 8-10 positions on average and turned over about 2x per year

**Is the alpha real?**

The factor analysis says: *probably, but not conclusively.*

- Alpha is 5.3% annualized with a t-stat of 1.92. This is close to the significance threshold of 2.0 but doesn't quite cross it. With more data (longer backtest period), it might become significant.
- The strategy has strong value exposure (HML loading 0.57, highly significant at t=7.34) and moderate momentum exposure (0.23, significant at t=3.45). These are the intended factor bets.
- Market beta is 0.78 — defensive, which helped during the 2022 rate-hiking drawdown.
- R-squared is 0.75 — about 75% of returns are explained by factors. The remaining 25% could be alpha or noise.

**Bottom line:** The strategy works, but much of the return comes from the value factor bet rather than genuine stock selection alpha. You're essentially buying cheap-with-momentum stocks and getting paid the value premium. That's not a bad thing — the value premium is real and persistent — but it means you could replicate ~75% of this return with factor ETFs (e.g., VLUE + MTUM).

If you want to increase the alpha component, consider:
1. A tighter value screen (PE < 10) to pick deeper value
2. Adding a quality filter to avoid value traps
3. Extending the backtest to 5+ years for more statistical power"
