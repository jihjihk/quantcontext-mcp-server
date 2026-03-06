"use client";

import { useState } from "react";
import { motion } from "framer-motion";

export function HostedTeaser() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;

    setStatus("loading");
    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!res.ok) throw new Error();
      setStatus("success");
      setEmail("");
    } catch {
      setStatus("error");
    }
  }

  return (
    <section
      className="border-t py-20"
      style={{ borderColor: "var(--border-default)", background: "var(--bg-surface)" }}
    >
      <div className="px-6 max-w-6xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span
            className="text-[11px] px-2.5 py-1 rounded-full border inline-block mb-6"
            style={{
              fontFamily: "var(--font-mono)",
              borderColor: "var(--color-accent)",
              color: "var(--color-accent)",
              background: "var(--color-accent-light)",
            }}
          >
            Launching soon
          </span>

          <h2
            className="text-3xl mb-4"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
          >
            Skip the build. Start trading.
          </h2>

          <p
            className="text-sm mb-8 max-w-xl mx-auto leading-relaxed"
            style={{ color: "var(--text-secondary)" }}
          >
            Your quant agent team, running 24/7. Strategies out of the box,
            portfolio monitoring, market screening. QuantContext computation
            built in. We're building a hosted version so you don't have to.
          </p>

          {status === "success" ? (
            <p
              className="text-sm py-2.5"
              style={{ fontFamily: "var(--font-mono)", color: "var(--color-positive)" }}
            >
              You're on the list. We'll be in touch.
            </p>
          ) : (
            <>
              <form onSubmit={handleSubmit} className="flex items-center justify-center gap-3 mb-2">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="text-sm px-4 py-2.5 rounded-md border outline-none w-64 transition-colors"
                  style={{
                    fontFamily: "var(--font-mono)",
                    borderColor: "var(--border-default)",
                    background: "var(--bg-page)",
                    color: "var(--text-primary)",
                  }}
                />
                <button
                  type="submit"
                  disabled={status === "loading"}
                  className="text-sm px-5 py-2.5 rounded-md transition-all cursor-pointer whitespace-nowrap disabled:opacity-60"
                  style={{
                    fontFamily: "var(--font-mono)",
                    background: "var(--color-accent)",
                    color: "#ffffff",
                  }}
                >
                  {status === "loading" ? "Joining..." : "Join waitlist"}
                </button>
                <a
                  href="https://x.com/ZommaLabs"
                  className="text-sm px-5 py-2.5 rounded-md border transition-colors whitespace-nowrap"
                  style={{
                    fontFamily: "var(--font-mono)",
                    borderColor: "var(--border-default)",
                    color: "var(--text-secondary)",
                  }}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Follow updates
                </a>
              </form>
              {status === "error" && (
                <p className="text-xs" style={{ color: "var(--color-negative)" }}>
                  Something went wrong. Try again.
                </p>
              )}
            </>
          )}
        </motion.div>
      </div>
    </section>
  );
}
