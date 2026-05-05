export default function Loading() {
  return (
    <div className="space-y-4">
      <div className="h-7 w-72 rounded bg-ink-800/60 animate-pulse" />
      <div className="h-4 w-[28rem] max-w-full rounded bg-ink-800/40 animate-pulse" />
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 mt-6">
        <div className="h-40 rounded-xl border border-ink-800 bg-ink-900/40 animate-pulse" />
        <div className="h-40 rounded-xl border border-ink-800 bg-ink-900/40 animate-pulse" />
      </div>
    </div>
  );
}
