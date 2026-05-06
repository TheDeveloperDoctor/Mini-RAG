"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ErrorBoundary } from "@/components/error-boundary";
import { evalRepo } from "@/lib/api/repositories/eval";
import { ApiError } from "@/lib/api/client";
import { METHOD_COLORS, METHOD_LABELS, formatBytes, formatMs } from "@/lib/utils";
import type { EvalMethodMetrics, EvalRunDTO } from "@/lib/types";

export default function EvalPage() {
  const [run, setRun] = useState<EvalRunDTO | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const latest = await evalRepo.latest();
      setRun(latest);
    } catch {
      /* swallow — page renders empty state */
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function trigger() {
    setRunning(true);
    setError(null);
    try {
      const latest = await evalRepo.run();
      setRun(latest);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Eval failed");
    } finally {
      setRunning(false);
    }
  }

  const winner = run ? pickBest(run.methods, "recall_at_5") : null;
  const fastest = run ? pickWorst(run.methods, "p50_latency_ms") : null;

  return (
    <div className="space-y-8">
      <section className="flex items-end justify-between flex-wrap gap-6">
        <div>
          <p className="font-mono text-[11px] tracking-[0.24em] uppercase text-mint">
            Eval harness · gold-set scoring
          </p>
          <h1 className="mt-2 text-[36px] font-semibold tracking-tight text-ink-100 leading-[1.05]">
            Numbers, not vibes.
          </h1>
          <p className="mt-3 max-w-xl text-ink-300 text-[15px] leading-relaxed">
            Each run measures every retriever against the gold set. Recall@k and MRR are the quality
            numbers; p50 / p95 are the speed numbers.{" "}
            <span className="text-ink-100">Both matter; neither alone wins.</span>
          </p>
        </div>
        <Button onClick={trigger} disabled={running}>
          {running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
          {running ? "Running…" : "Run eval"}
        </Button>
      </section>

      {error && (
        <div className="rounded-2xl border border-amber/30 bg-amber/[0.06] px-4 py-3 text-sm text-amber">
          {error}
        </div>
      )}

      <ErrorBoundary>
        {!run ? (
          <Empty />
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {winner && (
                <KPI
                  label="winner"
                  value={METHOD_LABELS[winner.method] ?? winner.method}
                  hue={METHOD_COLORS[winner.method] ?? "#6EE7B7"}
                  sub={`R@5 ${winner.recall_at_5.toFixed(3)}`}
                />
              )}
              {fastest && (
                <KPI
                  label="fastest"
                  value={METHOD_LABELS[fastest.method] ?? fastest.method}
                  hue={METHOD_COLORS[fastest.method] ?? "#FBBF24"}
                  sub={`p50 ${formatMs(fastest.p50_latency_ms)}`}
                />
              )}
              <KPI
                label="corpus"
                value={run.corpus_size.toLocaleString()}
                hue="#A78BFA"
                sub={`run #${run.id}`}
              />
            </div>

            <ResultsTable run={run} winner={winner} fastest={fastest} />

            <div className="font-mono text-[11px] text-ink-600 flex justify-between">
              <span>gold set · apps/api/src/eval/gold.jsonl</span>
              <span>{run.created_at}</span>
            </div>
          </div>
        )}
      </ErrorBoundary>
    </div>
  );
}

function Empty() {
  return (
    <div className="rounded-2xl border border-dashed border-white/[0.08] bg-white/[0.02] p-10 text-center">
      <p className="font-mono text-[10px] tracking-[0.2em] uppercase text-ink-600">no run yet</p>
      <p className="mt-2 text-sm text-ink-400">
        Click <span className="text-mint">Run eval</span> above to score every retriever against the gold set.
      </p>
    </div>
  );
}

function KPI({
  label,
  value,
  sub,
  hue,
}: {
  label: string;
  value: string;
  sub: string;
  hue: string;
}) {
  return (
    <div
      className="rounded-2xl border bg-panel-gradient p-5 shadow-panel"
      style={{ borderColor: `${hue}33`, backgroundImage: `linear-gradient(180deg, ${hue}10 0%, transparent 60%)` }}
    >
      <div
        className="font-mono text-[10px] tracking-[0.2em] uppercase"
        style={{ color: hue }}
      >
        {label}
      </div>
      <div className="mt-2 text-xl font-semibold text-ink-100 tracking-tight">{value}</div>
      <div className="mt-1 font-mono text-xs text-ink-400">{sub}</div>
    </div>
  );
}

function ResultsTable({
  run,
  winner,
  fastest,
}: {
  run: EvalRunDTO;
  winner: EvalMethodMetrics | null;
  fastest: EvalMethodMetrics | null;
}) {
  const winnerR5 = winner?.recall_at_5 ?? 1;
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-panel-gradient shadow-panel overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/[0.06]">
              <Th align="left">Method</Th>
              <Th align="right">Recall@5</Th>
              <Th align="right">Recall@10</Th>
              <Th align="right">MRR</Th>
              <Th align="right">p50</Th>
              <Th align="right">p95</Th>
              <Th align="right">Build</Th>
              <Th align="right">Index</Th>
            </tr>
          </thead>
          <tbody>
            {run.methods.map((m) => {
              const hue = METHOD_COLORS[m.method] ?? "#A3B0C7";
              const isWinner = winner?.method === m.method;
              const isFastest = fastest?.method === m.method;
              return (
                <tr
                  key={m.method}
                  className="border-b border-white/[0.04] last:border-0"
                  style={{ background: isWinner ? "rgba(110,231,183,0.04)" : undefined }}
                >
                  <Td align="left">
                    <div className="flex items-center gap-2.5">
                      <span
                        className="h-2 w-2 rounded-full shrink-0"
                        style={{ background: hue, boxShadow: `0 0 10px ${hue}99` }}
                      />
                      <span className="font-medium text-ink-100">
                        {METHOD_LABELS[m.method] ?? m.method}
                      </span>
                      {isWinner && (
                        <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-mint">
                          ★ winner
                        </span>
                      )}
                      {isFastest && !isWinner && (
                        <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-amber">
                          ⚡ fastest
                        </span>
                      )}
                    </div>
                  </Td>
                  <Td align="right" mono>
                    <BarCell value={m.recall_at_5} pct={m.recall_at_5 / winnerR5} hue={hue} highlight={isWinner} />
                  </Td>
                  <Td align="right" mono>{m.recall_at_10.toFixed(3)}</Td>
                  <Td align="right" mono>{m.mrr.toFixed(3)}</Td>
                  <Td align="right" mono highlight={isFastest}>{formatMs(m.p50_latency_ms)}</Td>
                  <Td align="right" mono>{formatMs(m.p95_latency_ms)}</Td>
                  <Td align="right" mono dim>{formatMs(m.build_ms)}</Td>
                  <Td align="right" mono dim>{formatBytes(m.index_size_bytes)}</Td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function BarCell({
  value,
  pct,
  hue,
  highlight,
}: {
  value: number;
  pct: number;
  hue: string;
  highlight?: boolean;
}) {
  return (
    <div className="inline-flex items-center gap-2.5 justify-end min-w-[120px]">
      <span className="inline-block w-[60px] h-1 rounded-full bg-white/[0.06] overflow-hidden">
        <span
          className="block h-full"
          style={{ width: `${Math.min(100, pct * 100)}%`, background: hue, boxShadow: `0 0 12px ${hue}` }}
        />
      </span>
      <span style={{ color: highlight ? hue : undefined, fontWeight: highlight ? 600 : 500 }}>
        {value.toFixed(3)}
      </span>
    </div>
  );
}

function Th({ children, align = "right" }: { children: React.ReactNode; align?: "left" | "right" }) {
  return (
    <th
      className={`px-4 py-3 font-mono text-[10px] tracking-[0.18em] uppercase text-ink-500 font-medium text-${align}`}
    >
      {children}
    </th>
  );
}

function Td({
  children,
  align = "right",
  mono,
  dim,
  highlight,
}: {
  children: React.ReactNode;
  align?: "left" | "right";
  mono?: boolean;
  dim?: boolean;
  highlight?: boolean;
}) {
  const colorClass = highlight ? "text-amber" : dim ? "text-ink-400" : "text-ink-100";
  return (
    <td
      className={`px-4 py-3.5 ${mono ? "font-mono text-[13px]" : "text-sm"} text-${align} ${colorClass}`}
    >
      {children}
    </td>
  );
}

function pickBest<K extends keyof EvalMethodMetrics>(
  methods: EvalMethodMetrics[],
  key: K,
): EvalMethodMetrics | null {
  if (methods.length === 0) return null;
  return methods.reduce((a, b) => ((b[key] as number) > (a[key] as number) ? b : a));
}

function pickWorst<K extends keyof EvalMethodMetrics>(
  methods: EvalMethodMetrics[],
  key: K,
): EvalMethodMetrics | null {
  if (methods.length === 0) return null;
  return methods.reduce((a, b) => ((b[key] as number) < (a[key] as number) ? b : a));
}
