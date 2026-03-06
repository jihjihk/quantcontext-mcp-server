"use client";

import { motion } from "framer-motion";

const STEPS = [
  {
    step: "01",
    label: "Screen",
    tool: "screen_stocks",
    prompt: "Find S&P 500 stocks with PE < 15, positive momentum",
    result: "23 matches \u00b7 Top: GILD (PE 12.3, Mom +18.4%)",
  },
  {
    step: "02",
    label: "Backtest",
    tool: "backtest_strategy",
    prompt: "Equal-weight top 5, monthly rebalance, 2 years",
    result: "Return +34.2% \u00b7 Sharpe 1.42 \u00b7 Max DD \u22128.7%",
  },
  {
    step: "03",
    label: "Decompose",
    tool: "analyze_factors",
    prompt: "Where is the alpha coming from?",
    result: "Alpha 4.7% (t=1.87) \u00b7 HML 0.49 \u00b7 R\u00b2 0.78",
  },
];

export function PipelineDemo() {
  return (
    <section
      className="border-t py-20"
      style={{ borderColor: "var(--border-default)", background: "var(--bg-surface)" }}
    >
      <div className="px-6 max-w-6xl mx-auto">
        <p
          className="text-[10px] uppercase tracking-[0.15em] mb-3"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
        >
          Try these prompts
        </p>
        <h2
          className="text-3xl mb-3"
          style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
        >
          ❯ From question to conviction.
        </h2>
        <p
          className="text-sm mb-12"
          style={{ color: "var(--text-secondary)" }}
        >
          Screen, backtest, decompose. Copy any prompt below into Claude.
        </p>

        <div className="flex flex-col md:flex-row gap-0">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.label}
              className="flex-1"
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.12 }}
            >
              <div
                className="p-6 border h-full"
                style={{
                  background: "var(--bg-page)",
                  borderColor: "var(--border-default)",
                  marginLeft: i > 0 ? "-1px" : 0,
                  borderRadius:
                    i === 0
                      ? "8px 0 0 8px"
                      : i === STEPS.length - 1
                        ? "0 8px 8px 0"
                        : "0",
                }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <span
                    className="text-[10px]"
                    style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
                  >
                    {step.step}
                  </span>
                  <span
                    className="text-[11px] px-2 py-0.5 rounded"
                    style={{
                      fontFamily: "var(--font-mono)",
                      background: "var(--color-accent-light)",
                      color: "var(--color-accent)",
                    }}
                  >
                    {step.tool}
                  </span>
                </div>

                <p
                  className="text-xs mb-4 leading-relaxed"
                  style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
                >
                  &ldquo;{step.prompt}&rdquo;
                </p>

                <div className="h-px mb-4" style={{ background: "var(--border-default)" }} />

                <p
                  className="text-xs font-medium"
                  style={{ fontFamily: "var(--font-mono)", color: "var(--color-positive)" }}
                >
                  {step.result}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.p
          className="text-xs mt-8 text-center"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          Every number above was computed from historical market data.
        </motion.p>
      </div>
    </section>
  );
}
