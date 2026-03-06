"use client";

import { motion } from "framer-motion";

const POINTS = [
  {
    title: "Agents hallucinate numbers",
    body: "Ask an LLM for a Sharpe ratio. Confident guess. Ask again, different number. QuantContext computes from real data. Same input, same output.",
  },
  {
    title: "Agents can't verify themselves",
    body: "AI agents skip steps, fabricate results, and report numbers they never computed. Trading agents need external, deterministic verification.",
  },
  {
    title: "No API keys required",
    body: "Public data only: Yahoo Finance and the Kenneth French Data Library. No account, no quotas, no billing.",
  },
];

export function WhySection() {
  return (
    <section
      className="border-y py-20"
      style={{ borderColor: "var(--border-default)", background: "var(--bg-surface)" }}
    >
      <div className="px-6 max-w-6xl mx-auto">
        <p
          className="text-[10px] uppercase tracking-[0.15em] mb-3"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
        >
          Why this exists
        </p>
        <h2
          className="text-3xl mb-4"
          style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
        >
          Built for systems that trade real money.
        </h2>
        <p
          className="text-sm mb-12"
          style={{ color: "var(--text-secondary)" }}
        >
          Data providers give agents eyes. Brokers give them hands.
          QuantContext gives them a brain.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {POINTS.map((item, i) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              <h3
                className="text-[19px] mb-2"
                style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
              >
                {item.title}
              </h3>
              <p
                className="text-sm leading-relaxed"
                style={{ color: "var(--text-secondary)" }}
              >
                {item.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
