"use client";

import { useState } from "react";
import { motion } from "framer-motion";

export function Hero() {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText("pip install quantcontext-mcp");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="px-6 pt-28 pb-20 max-w-6xl mx-auto">
      {/* Badge */}
      <motion.div
        className="flex items-center gap-2.5 mb-8"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <span
          className="text-[11px] px-2.5 py-1 rounded-full border"
          style={{
            fontFamily: "var(--font-mono)",
            borderColor: "var(--color-accent)",
            color: "var(--color-accent)",
            background: "var(--color-accent-light)",
          }}
        >
          Open Source MCP Server
        </span>
        <span
          className="text-[11px]"
          style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
        >
          No signup. No API keys. No config.
        </span>
      </motion.div>

      <div className="flex flex-col lg:flex-row items-start gap-14">
        {/* Left column */}
        <div className="flex-1 space-y-6">
          <motion.h1
            className="text-4xl lg:text-[52px] leading-[1.1] tracking-tight"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.05 }}
          >
            Give your trading agent
            <br />
            a quant brain.
          </motion.h1>

          <motion.p
            className="text-[15px] leading-relaxed max-w-lg"
            style={{ color: "var(--text-secondary)" }}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.12 }}
          >
            QuantContext is an MCP server that gives AI agents real
            quant computation: stock screening, strategy backtesting,
            and Fama-French factor analysis. Every number is computed
            from real market data, using proven models. Ground your
            trading agent in math.
            <br className="hidden sm:block" />
            <span className="mt-1 inline-block">
              Works with Claude, Codex, and any MCP client.
            </span>
          </motion.p>

          {/* Install snippet */}
          <motion.div
            className="flex items-center gap-2 px-4 py-3 rounded-lg max-w-md"
            style={{ background: "#1e293b" }}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <span
              className="text-sm select-none font-mono"
              style={{ color: "rgba(255,255,255,0.4)" }}
            >
              $
            </span>
            <code
              className="text-sm flex-1 font-mono"
              style={{ color: "rgba(255,255,255,0.85)" }}
            >
              pip install quantcontext-mcp
            </code>
            <button
              onClick={handleCopy}
              className="text-xs px-2.5 py-1 rounded transition-all cursor-pointer font-mono"
              style={{
                color: copied ? "#4ade80" : "rgba(255,255,255,0.5)",
                background: copied ? "rgba(74,222,128,0.1)" : "rgba(255,255,255,0.08)",
              }}
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </motion.div>

          <motion.p
            className="text-xs font-mono"
            style={{ color: "var(--text-tertiary)" }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.28 }}
          >
            or:{" "}
            <code style={{ color: "var(--text-secondary)" }}>
              claude mcp add quantcontext -- quantcontext
            </code>
          </motion.p>

          {/* CTAs */}
          <motion.div
            className="flex gap-3"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <a
              href="http://localhost:3333"
              className="text-sm px-5 py-2.5 rounded-md transition-all"
              style={{
                fontFamily: "var(--font-mono)",
                background: "var(--color-accent)",
                color: "#ffffff",
              }}
            >
              View Docs
            </a>
            <a
              href="https://github.com/jihjihk/quantcontext-mcp-server"
              className="text-sm px-5 py-2.5 rounded-md border transition-colors"
              style={{
                fontFamily: "var(--font-mono)",
                borderColor: "var(--border-default)",
                color: "var(--text-secondary)",
                background: "var(--bg-surface)",
              }}
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </motion.div>
        </div>

        {/* Right column: terminal preview */}
        <motion.div
          className="flex-1 w-full max-w-xl"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="terminal">
            <div className="terminal-chrome">
              <div className="terminal-dot" style={{ background: "#ef4444" }} />
              <div className="terminal-dot" style={{ background: "#eab308" }} />
              <div className="terminal-dot" style={{ background: "#22c55e" }} />
              <span
                className="ml-3 text-[11px]"
                style={{ fontFamily: "var(--font-mono)", color: "rgba(255,255,255,0.35)" }}
              >
                claude
              </span>
            </div>
            <div className="terminal-body">
              <div>
                <p className="text-[13px]" style={{ fontFamily: "var(--font-mono)", color: "rgba(255,255,255,0.5)" }}>
                  &gt; Screen S&amp;P 500 for value stocks with positive momentum
                </p>
              </div>
              <div>
                <span
                  className="inline-block text-[10px] px-2 py-0.5 rounded mb-2"
                  style={{
                    fontFamily: "var(--font-mono)",
                    background: "rgba(37,99,235,0.2)",
                    color: "#60a5fa",
                  }}
                >
                  screen_stocks
                </span>
                <div
                  className="text-[12px] leading-relaxed"
                  style={{ fontFamily: "var(--font-mono)", color: "rgba(255,255,255,0.7)" }}
                >
                  <p style={{ color: "rgba(255,255,255,0.4)" }}>Found 23 matches. Top 5:</p>
                  <table className="mt-2 w-full">
                    <thead>
                      <tr style={{ color: "rgba(255,255,255,0.35)" }}>
                        <td className="pr-4">TICKER</td>
                        <td className="pr-4">PE</td>
                        <td className="pr-4">MOM_6M</td>
                        <td>SCORE</td>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        ["GILD", "12.3", "+18.4%", "0.84"],
                        ["VZ", "8.7", "+12.1%", "0.71"],
                        ["MO", "9.1", "+9.8%", "0.68"],
                      ].map(([t, pe, mom, s]) => (
                        <tr key={t}>
                          <td className="pr-4" style={{ color: "#e2e8f0" }}>{t}</td>
                          <td className="pr-4">{pe}</td>
                          <td className="pr-4" style={{ color: "#4ade80" }}>{mom}</td>
                          <td>{s}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Stats strip */}
      <motion.div
        className="mt-16 pt-8 border-t grid grid-cols-3 gap-6"
        style={{ borderColor: "var(--border-default)" }}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        {[
          { value: "~550", label: "stocks covered" },
          { value: "99", label: "years of factor data" },
          { value: "7", label: "screening methods" },
        ].map((stat) => (
          <div key={stat.label}>
            <div
              className="text-2xl font-medium"
              style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
            >
              {stat.value}
            </div>
            <div
              className="text-xs mt-0.5"
              style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
            >
              {stat.label}
            </div>
          </div>
        ))}
      </motion.div>
    </section>
  );
}
