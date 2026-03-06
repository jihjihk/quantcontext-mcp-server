import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QuantContext — Deterministic Quant Tools for AI Agents",
  description:
    "MCP server for stock screening, backtesting, and factor analysis. Every number computed from real market data, not generated.",
  openGraph: {
    title: "QuantContext — Quant Tools for AI Trading Agents",
    description:
      "The MCP server that gives AI agents real quant computation. Screen stocks, backtest strategies, run factor analysis.",
    type: "website",
    url: "https://quantcontext.ai",
  },
  twitter: {
    card: "summary_large_image",
    title: "QuantContext — Quant Tools for AI Trading Agents",
    description:
      "Deterministic computation for AI trading agents. MCP server with 3 quant tools.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
