"use client";

import { useState } from "react";

const DOCS_URL = process.env.NEXT_PUBLIC_DOCS_URL || "https://docs.quantcontext.ai";

const LINKS = [
  { label: "Tools", href: "#tools" },
  { label: "Docs", href: DOCS_URL, external: true },
  { label: "GitHub", href: "https://github.com/jihjihk/quantcontext-mcp-server", external: true },
];

export function Nav() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b"
      style={{
        background: "rgba(250,250,250,0.85)",
        borderColor: "var(--border-default)",
      }}
    >
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <a href="/">
          <img src="/logo.svg" alt="QuantContext" className="h-5 w-auto" />
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-6">
          {LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-[13px] transition-colors hover:text-[var(--text-primary)]"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--text-secondary)",
              }}
              {...(link.external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
            >
              {link.label}
            </a>
          ))}
          <a
            href="#install"
            className="text-[13px] px-3.5 py-1.5 rounded-md transition-all"
            style={{
              fontFamily: "var(--font-mono)",
              background: "var(--text-primary)",
              color: "white",
            }}
          >
            Install
          </a>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden p-1"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            {mobileOpen ? (
              <path d="M5 5l10 10M15 5l-10 10" stroke="var(--text-primary)" strokeWidth="1.5" />
            ) : (
              <>
                <path d="M3 6h14M3 10h14M3 14h14" stroke="var(--text-primary)" strokeWidth="1.5" />
              </>
            )}
          </svg>
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div
          className="md:hidden border-t px-6 py-4 space-y-3"
          style={{ borderColor: "var(--border-default)", background: "var(--bg-surface)" }}
        >
          {LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="block text-sm"
              style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </a>
          ))}
        </div>
      )}
    </nav>
  );
}
