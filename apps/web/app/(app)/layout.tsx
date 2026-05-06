import Link from "next/link";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen text-ink-100">
      <header className="sticky top-0 z-20 border-b border-white/[0.06] bg-bg/80 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full rounded-full bg-mint opacity-60 animate-pulse-dot" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-mint shadow-glow-mint" />
            </span>
            <span className="font-semibold tracking-tight text-ink-100">
              Mini RAG
              <span className="ml-2 text-xs font-mono uppercase tracking-[0.18em] text-ink-500 group-hover:text-mint/80 transition-colors">
                comparison lab
              </span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-6 font-mono text-[11px] text-ink-400">
            <Telemetry label="STATUS" value="LIVE" tone="mint" />
            <Telemetry label="MODEL" value="bge-small" />
            <Telemetry label="EMBED" value="384-D" />
          </div>

          <nav className="text-sm text-ink-300 flex items-center gap-1">
            <NavLink href="/">Lab</NavLink>
            <NavLink href="/eval">Eval</NavLink>
            <a
              href="https://github.com/TheDeveloperDoctor/Mini-RAG"
              className="px-3 py-1.5 rounded-full hover:bg-white/[0.04] hover:text-ink-100 transition-colors"
              rel="noreferrer noopener"
              target="_blank"
            >
              GitHub
            </a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-10">{children}</main>

      <footer className="border-t border-white/[0.06] mt-20">
        <div className="mx-auto max-w-7xl px-6 py-6 flex flex-wrap justify-between items-center gap-3 text-xs text-ink-500 font-mono">
          <span>Local embeddings · BAAI/bge-small-en-v1.5</span>
          <span className="text-ink-600">Built to be measured, not impressive.</span>
        </div>
      </footer>
    </div>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="px-3 py-1.5 rounded-full hover:bg-white/[0.04] hover:text-ink-100 transition-colors"
    >
      {children}
    </Link>
  );
}

function Telemetry({ label, value, tone }: { label: string; value: string; tone?: "mint" }) {
  return (
    <div className="flex flex-col items-end leading-none">
      <span className="text-[9px] tracking-[0.2em] text-ink-600">{label}</span>
      <span
        className={`text-xs font-semibold mt-0.5 ${tone === "mint" ? "text-mint" : "text-ink-200"}`}
      >
        {value}
      </span>
    </div>
  );
}
