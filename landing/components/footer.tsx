const DOCS_URL = process.env.NEXT_PUBLIC_DOCS_URL || "https://docs.quantcontext.ai";

export function Footer() {
  return (
    <footer
      className="px-6 py-14 border-t"
      style={{ borderColor: "var(--border-default)", background: "var(--bg-surface)" }}
    >
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          <div className="col-span-2 md:col-span-1">
            <div className="mb-2">
              <img src="/logo.svg" alt="QuantContext" className="h-5 w-auto" />
            </div>
            <p
              className="text-xs leading-relaxed"
              style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
            >
              The computation layer
              <br />
              for AI trading agents.
            </p>
          </div>

          <div>
            <span
              className="text-[10px] uppercase tracking-[0.15em] block mb-4"
              style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
            >
              Developers
            </span>
            <div className="space-y-2.5">
              {[
                { label: "Documentation", href: DOCS_URL },
                { label: "Quickstart", href: `${DOCS_URL}/quickstart` },
                { label: "Methodology", href: `${DOCS_URL}/methodology` },
              ].map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-xs block transition-colors hover:text-[var(--text-primary)]"
                  style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>

          <div>
            <span
              className="text-[10px] uppercase tracking-[0.15em] block mb-4"
              style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
            >
              Resources
            </span>
            <div className="space-y-2.5">
              {[
                { label: "GitHub", href: "https://github.com/jihjihk/quantcontext-mcp-server" },
                { label: "PyPI", href: "https://pypi.org/project/quantcontext-mcp/" },
                { label: "Changelog", href: "https://github.com/jihjihk/quantcontext-mcp-server/releases" },
              ].map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-xs block transition-colors hover:text-[var(--text-primary)]"
                  style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>

          <div>
            <span
              className="text-[10px] uppercase tracking-[0.15em] block mb-4"
              style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
            >
              Company
            </span>
            <div className="space-y-2.5">
              {[
                { label: "Zomma", href: "https://zommalabs.com" },
                { label: "X", href: "https://x.com/ZommaLabs" },
              ].map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-xs block transition-colors hover:text-[var(--text-primary)]"
                  style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="h-px mb-6" style={{ background: "var(--border-default)" }} />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
          <p
            className="text-xs"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
          >
            Built by Zomma &middot; 2026
          </p>
          <p
            className="text-xs"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-tertiary)" }}
          >
            pip install quantcontext-mcp
          </p>
        </div>
      </div>
    </footer>
  );
}
