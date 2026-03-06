"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const TOOLS = [
  {
    name: "screen_stocks",
    label: "Stock Screener",
    description:
      "Filter S&P 500, Russell 2000, or Nasdaq 100 by fundamental, technical, and momentum criteria. 7 screen types.",
    example: {
      input: `{
  "universe": "sp500",
  "screen_type": "value_screen",
  "config": { "pe_lt": 15, "roe_gt": 12 }
}`,
      output: `{
  "count": 23,
  "results": [
    { "ticker": "GILD", "pe_ratio": 12.3, "score": 0.84 },
    { "ticker": "MOS",  "pe_ratio": 8.1,  "score": 0.79 }
  ]
}`,
    },
  },
  {
    name: "backtest_strategy",
    label: "Strategy Backtester",
    description:
      "Rebalance-loop engine with multi-stage pipelines, stop-loss, position limits, and drawdown circuit breaker.",
    example: {
      input: `{
  "stages": [
    { "skill": "value_screen", "config": { "pe_lt": 15 } }
  ],
  "rebalance": "monthly",
  "stop_loss": 0.15
}`,
      output: `{
  "metrics": {
    "cagr": 0.1012,
    "sharpe": 1.24,
    "max_drawdown": -0.1483
  },
  "equity_curve": [...]
}`,
    },
  },
  {
    name: "analyze_factors",
    label: "Factor Analysis",
    description:
      "Fama-French 4-factor decomposition: market, size, value, momentum. Alpha with t-stat and R-squared.",
    example: {
      input: `{
  "equity_curve": [
    { "date": "2023-01-03", "value": 100000 },
    ...
  ]
}`,
      output: `{
  "alpha_annualized": 0.0469,
  "alpha_tstat": 1.87,
  "factors": {
    "HML": { "loading": 0.49, "tstat": 5.67 }
  },
  "r_squared": 0.78
}`,
    },
  },
];

export function ToolsGrid() {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <section id="tools" className="px-6 py-20 max-w-6xl mx-auto">
      <p
        className="text-[10px] uppercase tracking-[0.15em] mb-3"
        style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
      >
        The tools
      </p>
      <h2
        className="text-3xl mb-3"
        style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
      >
        Three tools today. More shipping soon.
      </h2>
      <p
        className="text-sm mb-12"
        style={{ color: "var(--text-secondary)" }}
      >
        Every number computed from real market data. Click a tool to see example I/O.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
        {TOOLS.map((tool, i) => (
          <motion.div
            key={tool.name}
            className="flex flex-col"
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.08 }}
          >
            <button
              onClick={() =>
                setExpanded(expanded === tool.name ? null : tool.name)
              }
              className="w-full text-left p-5 rounded-lg border transition-all cursor-pointer flex flex-col flex-1"
              style={{
                borderColor:
                  expanded === tool.name
                    ? "var(--color-accent)"
                    : "var(--border-default)",
                background:
                  expanded === tool.name
                    ? "var(--color-accent-light)"
                    : "var(--bg-surface)",
              }}
            >
              <code
                className="text-[11px] mb-2 block"
                style={{ fontFamily: "var(--font-mono)", color: "var(--color-accent)" }}
              >
                {tool.name}
              </code>
              <h3
                className="text-[19px] mb-2"
                style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
              >
                {tool.label}
              </h3>
              <p
                className="text-sm leading-relaxed flex-1"
                style={{ color: "var(--text-secondary)" }}
              >
                {tool.description}
              </p>
              <span
                className="text-xs mt-4 block"
                style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
              >
                {expanded === tool.name ? "Hide example \u2191" : "See example \u2193"}
              </span>
            </button>

            <AnimatePresence>
              {expanded === tool.name && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="code-example mt-1">
                    <div className="code-section">
                      <div className="code-label">Input</div>
                      <pre>{tool.example.input}</pre>
                    </div>
                    <div className="divider" />
                    <div className="code-section output">
                      <div className="code-label">Output</div>
                      <pre>{tool.example.output}</pre>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

    </section>
  );
}
