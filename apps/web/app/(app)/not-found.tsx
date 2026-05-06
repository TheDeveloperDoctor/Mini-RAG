import Link from "next/link";

export default function NotFound() {
  return (
    <div className="text-center max-w-md mx-auto mt-20 space-y-4">
      <p className="font-mono text-[10px] tracking-[0.24em] uppercase text-mint">404</p>
      <h2 className="text-3xl font-semibold tracking-tight text-ink-100">Page not found</h2>
      <p className="text-sm text-ink-400">
        That route doesn&apos;t exist. Maybe you meant the lab or the eval page.
      </p>
      <div className="flex justify-center gap-3 pt-2">
        <Link
          href="/"
          className="inline-flex items-center gap-2 h-10 px-5 rounded-full text-sm font-medium text-bg bg-gradient-to-b from-mint to-mint-dim shadow-glow-mint hover:brightness-110 transition-all"
        >
          Lab
        </Link>
        <Link
          href="/eval"
          className="inline-flex items-center gap-2 h-10 px-5 rounded-full text-sm font-medium text-ink-100 bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] transition-colors"
        >
          Eval
        </Link>
      </div>
    </div>
  );
}
