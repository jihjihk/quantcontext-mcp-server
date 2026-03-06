"use client";

import { useState } from "react";
import { motion } from "framer-motion";

const INSTALL_METHODS = [
  { label: "pip", command: "pip install quantcontext-mcp" },
  { label: "Claude Desktop", command: "claude mcp add quantcontext -- quantcontext" },
];

export function InstallSection() {
  const [copied, setCopied] = useState<number | null>(null);

  const handleCopy = (cmd: string, idx: number) => {
    navigator.clipboard.writeText(cmd);
    setCopied(idx);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <section id="install" className="px-6 py-20 max-w-6xl mx-auto">
      <div className="max-w-2xl mx-auto text-center">
        <motion.h2
          className="text-4xl mb-4"
          style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          Start in 30 seconds.
        </motion.h2>
        <motion.p
          className="text-sm mb-10"
          style={{ color: "var(--text-secondary)" }}
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.05 }}
        >
          Install the package and connect it to your AI agent. No API keys, no
          configuration, no account required. Works with any MCP-compatible client.
        </motion.p>

        <motion.div
          className="space-y-3"
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
        >
          {INSTALL_METHODS.map((method, i) => (
            <div
              key={method.label}
              className="flex items-center gap-3 px-4 py-3.5 rounded-lg"
              style={{ background: "#1e293b" }}
            >
              <span
                className="text-[10px] uppercase tracking-wider w-28 text-left shrink-0 font-mono"
                style={{ color: "rgba(255,255,255,0.35)" }}
              >
                {method.label}
              </span>
              <code
                className="text-sm flex-1 text-left font-mono"
                style={{ color: "rgba(255,255,255,0.85)" }}
              >
                {method.command}
              </code>
              <button
                onClick={() => handleCopy(method.command, i)}
                className="text-xs px-3 py-1 rounded transition-all cursor-pointer shrink-0 font-mono"
                style={{
                  color: copied === i ? "#4ade80" : "rgba(255,255,255,0.5)",
                  background: copied === i ? "rgba(74,222,128,0.1)" : "rgba(255,255,255,0.08)",
                }}
              >
                {copied === i ? "Copied!" : "Copy"}
              </button>
            </div>
          ))}
        </motion.div>

        <motion.div
          className="flex justify-center gap-6 mt-10"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
        >
          <a
            href="http://localhost:3333"
            className="text-sm underline underline-offset-4 decoration-1 transition-colors"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
            target="_blank"
            rel="noopener noreferrer"
          >
            Documentation
          </a>
          <a
            href="https://github.com/jihjihk/quantcontext-mcp-server"
            className="text-sm underline underline-offset-4 decoration-1 transition-colors"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <a
            href="https://pypi.org/project/quantcontext-mcp/"
            className="text-sm underline underline-offset-4 decoration-1 transition-colors"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
            target="_blank"
            rel="noopener noreferrer"
          >
            PyPI
          </a>
        </motion.div>
      </div>
    </section>
  );
}
