"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ErrorBoundary } from "@/components/error-boundary";
import { evalRepo } from "@/lib/api/repositories/eval";
import { ApiError } from "@/lib/api/client";
import { METHOD_LABELS, formatBytes, formatMs } from "@/lib/utils";
import type { EvalRunDTO } from "@/lib/types";

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

  return (
    <div className="space-y-6">
      <section className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink-100">Eval Harness</h1>
          <p className="text-sm text-ink-400 mt-1 max-w-3xl">
            Each run measures every retriever against the gold set. Recall@k and MRR are the
            quality numbers; p50 / p95 are the speed numbers.
          </p>
        </div>
        <Button onClick={trigger} disabled={running}>
          {running ? <Loader2 className="h-3 w-3 animate-spin" /> : <Play className="h-3 w-3" />}
          {running ? "Running…" : "Run eval"}
        </Button>
      </section>

      {error && (
        <div className="rounded-md border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm text-amber-200">
          {error}
        </div>
      )}

      <ErrorBoundary>
        <ResultsCard run={run} />
      </ErrorBoundary>
    </div>
  );
}

function ResultsCard({ run }: { run: EvalRunDTO | null }) {
  if (!run) {
    return (
      <div className="rounded-xl border border-dashed border-ink-800 p-10 text-center text-sm text-ink-500">
        No eval run yet. Click <span className="text-ink-300">Run eval</span> above.
      </div>
    );
  }
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-medium text-ink-100">Run #{run.id}</h3>
          <Badge tone="accent">corpus_size {run.corpus_size}</Badge>
        </div>
        <span className="text-xs font-mono text-ink-500">{run.created_at}</span>
      </CardHeader>
      <CardBody>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-[11px] uppercase tracking-wider text-ink-500">
              <tr className="border-b border-ink-800">
                <Th align="left">method</Th>
                <Th>recall@5</Th>
                <Th>recall@10</Th>
                <Th>mrr</Th>
                <Th>p50</Th>
                <Th>p95</Th>
                <Th>build</Th>
                <Th>size</Th>
              </tr>
            </thead>
            <tbody className="font-mono text-ink-200">
              {run.methods.map((m) => (
                <tr key={m.method} className="border-b border-ink-800/60 last:border-0">
                  <Td align="left">{METHOD_LABELS[m.method] ?? m.method}</Td>
                  <Td>{m.recall_at_5.toFixed(3)}</Td>
                  <Td>{m.recall_at_10.toFixed(3)}</Td>
                  <Td>{m.mrr.toFixed(3)}</Td>
                  <Td>{formatMs(m.p50_latency_ms)}</Td>
                  <Td>{formatMs(m.p95_latency_ms)}</Td>
                  <Td>{formatMs(m.build_ms)}</Td>
                  <Td>{formatBytes(m.index_size_bytes)}</Td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardBody>
    </Card>
  );
}

function Th({ children, align = "right" }: { children: React.ReactNode; align?: "left" | "right" }) {
  return <th className={`px-3 py-2 text-${align}`}>{children}</th>;
}

function Td({ children, align = "right" }: { children: React.ReactNode; align?: "left" | "right" }) {
  return <td className={`px-3 py-2 text-${align}`}>{children}</td>;
}
