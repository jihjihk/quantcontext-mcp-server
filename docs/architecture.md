# QuantContext Architecture

## The LLM Boundary

QuantContext enforces a strict boundary between what LLMs do and what code does:

```
+-----------------------------------------------------------+
|                        LLM Layer                          |
|  - Parses user intent ("find cheap stocks")               |
|  - Selects the right tool (screen_stocks)                 |
|  - Chooses parameters ({pe_lt: 15})                       |
|  - Explains results in natural language                   |
|  - Decides what to compute next                           |
|                                                           |
|  The LLM NEVER computes a number.                         |
|  The LLM NEVER touches market data.                       |
|  The LLM NEVER estimates a Sharpe ratio.                  |
+--------------------------+--------------------------------+
                           | MCP Protocol (JSON-RPC over stdio)
                           |
+--------------------------v--------------------------------+
|                   QuantContext Layer                       |
|  - Receives structured tool calls                         |
|  - Validates inputs                                       |
|  - Executes deterministic Python computation              |
|  - Returns structured JSON                                |
|                                                           |
|  Every number is computed from data.                      |
|  Same input always produces same output.                  |
|  No LLM calls in the computation path.                    |
+--------------------------+--------------------------------+
                           |
+--------------------------v--------------------------------+
|                      Data Layer                           |
|  - yfinance: daily OHLCV, fundamentals                    |
|  - Kenneth French Data Library: Fama-French factors       |
|  - Local cache: ~/.quantcontext/cache/                    |
|  - Bundled universe lists: S&P 500, Russell 2000, Nasdaq  |
+-----------------------------------------------------------+
```

## Why Determinism Matters for Trading

LLMs hallucinate numbers. QuantContext ensures every number returned to an agent is:
1. **Computed from actual market data** — not generated, estimated, or hallucinated
2. **Deterministic** — same inputs produce identical outputs, always
3. **Auditable** — the computation path is pure Python with no randomness (except Monte Carlo, which accepts an explicit seed)

The LLM's job is to decide *what* to compute. Python's job is to compute it. The LLM then explains the results. At no point does the LLM touch a number.

## How the Tools Work

### screen_stocks

```
User query -> LLM selects screen_type and config
                     |
                     v
         +----------------------+
         |  get_universe(date)  |  <- Fetches/caches ticker list + fundamentals
         +----------+-----------+
                    |
                    v
         +----------------------+
         |  execute_pipeline()  |  <- Runs screen skill on DataFrame
         |  SKILL_REGISTRY[     |     Filters, ranks, scores
         |    screen_type]      |
         +----------+-----------+
                    |
                    v
         +----------------------+
         |  JSON serialization  |  <- Clean records, NaN -> null, top 30
         +----------------------+
```

The engine module `pipeline_executor.py` maps pipeline stages to skill functions from `SKILL_REGISTRY`. Each skill receives a pandas DataFrame and returns a filtered/ranked DataFrame. Stages execute sequentially — the output of stage N is the input to stage N+1.

### backtest_strategy

```
Pipeline spec -> rebalance dates generated
                     |
                     v
         +----------------------+
         |  For each rebalance  |
         |  date:               |
         |  1. Run pipeline     |  <- Same execute_pipeline() as screening
         |  2. Size positions   |  <- equal_weight or inverse_volatility
         |  3. Enforce limits   |  <- max_position_size cap
         |  4. Execute trades   |  <- Buy/sell to target weights
         |  5. Check stop-loss  |  <- Daily per-position check
         |  6. Check drawdown   |  <- Circuit breaker
         +----------+-----------+
                    |
                    v
         +----------------------+
         |  Daily P&L tracking  |  <- Mark-to-market all positions
         |  Equity curve        |
         |  Trade log           |
         +----------+-----------+
                    |
                    v
         +----------------------+
         |  Metrics computation |  <- CAGR, Sharpe, max DD, Calmar,
         |                      |     win rate, turnover
         +----------------------+
```

The backtest engine (`backtest_engine.py`) is a rebalance-loop engine. On each rebalance date, it re-runs the full screening pipeline, determines target portfolio weights, and executes trades to move from current to target weights. Between rebalance dates, it tracks daily P&L and enforces risk controls (stop-loss, drawdown circuit breaker).

### factor_analysis

```
Equity curve -> daily returns
                    |
                    v
         +----------------------+
         |  Load Fama-French    |  <- Downloads from Kenneth French Data Library
         |  factors for period  |     Caches locally after first download
         +----------+-----------+
                    |
                    v
         +----------------------+
         |  OLS Regression      |  <- y = alpha + b1*MktRF + b2*SMB
         |  (numpy, no          |       + b3*HML + b4*Mom + epsilon
         |   statsmodels)       |
         +----------+-----------+
                    |
                    v
         +----------------------+
         |  Compute t-stats,    |  <- Manual computation from (X'X)^-1
         |  R-squared,          |     No external statistics library needed
         |  residual vol        |
         +----------------------+
```

The factor regression (`factor_analysis.py`) uses manual OLS via numpy linear algebra. This avoids a statsmodels dependency while producing identical results. The regression decomposes excess returns (portfolio return minus risk-free rate) into four systematic factors.

## Data Sources and Caching

| Source | Data | Cache TTL | Cache Location |
|--------|------|-----------|----------------|
| yfinance | Daily OHLCV prices | 1 day | `~/.quantcontext/cache/prices/` |
| yfinance | Fundamentals (PE, ROE, etc.) | 7 days | `~/.quantcontext/cache/fundamentals/` |
| Kenneth French | Fama-French factors + momentum | 30 days | `~/.quantcontext/cache/factors/` |
| Bundled | Universe constituent lists | Package version | Installed with package |

**First-call performance:** The first call to any tool downloads market data (~10s for S&P 500). Subsequent calls use the cache and complete in <1s (screen) or 3-8s (backtest).

**Total disk usage:** ~50MB for full S&P 500 coverage.

**No API keys required.** yfinance uses public Yahoo Finance endpoints. Kenneth French data is freely available. Universe lists are bundled in the package.

## Transport

QuantContext uses the MCP stdio transport. The server reads JSON-RPC messages from stdin and writes responses to stdout. This is the simplest transport — no HTTP server, no ports, no authentication.

```bash
# The server is started by the MCP client (Claude Desktop, Claude Code, etc.)
# You never need to run it manually
quantcontext  # Entry point defined in pyproject.toml [project.scripts]
```

For development/testing, you can also import and call the tools directly:
```python
from quantcontext.server import screen_stocks, backtest_strategy, factor_analysis
import asyncio, json

result = asyncio.run(screen_stocks(universe="sp500", screen_type="value_screen"))
print(json.loads(result))
```
