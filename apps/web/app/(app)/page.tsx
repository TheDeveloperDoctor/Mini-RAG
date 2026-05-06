"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { UploadPanel } from "@/components/upload-panel";
import { QueryBox } from "@/components/query-box";
import { AnswerColumn } from "@/components/answer-column";
import { LatencyChart } from "@/components/latency-chart";
import { ErrorBoundary } from "@/components/error-boundary";
import { AnswerColumnSkeleton } from "@/components/ui/skeleton";
import { documentsRepo } from "@/lib/api/repositories/documents";
import { queryRepo } from "@/lib/api/repositories/query";
import { ApiError } from "@/lib/api/client";
import type { DocumentDTO, MethodResult, QueryResponse } from "@/lib/types";

export default function HomePage() {
  const [documents, setDocuments] = useState<DocumentDTO[]>([]);
  const [history, setHistory] = useState<QueryResponse[]>([]);
  const [latest, setLatest] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshDocuments = useCallback(async () => {
    try {
      const docs = await documentsRepo.list();
      setDocuments(docs);
    } catch (err) {
      console.error("failed to load documents", err);
    }
  }, []);

  useEffect(() => {
    void refreshDocuments();
  }, [refreshDocuments]);

  async function handleQuery(question: string, topK: number, synthesize: boolean) {
    setLoading(true);
    setError(null);
    try {
      const response = await queryRepo.run({
        question,
        top_k: topK,
        synthesize_answer: synthesize,
      });
      setLatest(response);
      setHistory((h) => [...h, response].slice(-25));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <section>
        <p className="font-mono text-[11px] tracking-[0.24em] uppercase text-mint">
          Retriever comparison lab
        </p>
        <h1 className="mt-2 text-[40px] font-semibold tracking-tight text-ink-100 leading-[1.05]">
          One question.{" "}
          <span className="text-ink-400">Five retrievers.</span>{" "}
          <span className="text-mint">Side by side.</span>
        </h1>
        <p className="mt-4 max-w-2xl text-ink-300 text-[15px] leading-relaxed">
          Look at the latency badges and the chunk scores — the cost of every retrieval choice is
          on the page. <span className="text-ink-100">No vibes. Receipts only.</span>
        </p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-5">
        <ErrorBoundary>
          <UploadPanel documents={documents} onUploaded={refreshDocuments} />
        </ErrorBoundary>
        <ErrorBoundary>
          <QueryBox loading={loading} onSubmit={handleQuery} />
        </ErrorBoundary>
      </div>

      {error && (
        <div className="rounded-2xl border border-amber/30 bg-amber/[0.06] px-4 py-3 text-sm text-amber flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <ErrorBoundary>
        <ResultsGrid latest={latest} loading={loading} />
      </ErrorBoundary>

      <ErrorBoundary>
        <LatencyChart history={history} />
      </ErrorBoundary>
    </div>
  );
}

function ResultsGrid({
  latest,
  loading,
}: {
  latest: QueryResponse | null;
  loading: boolean;
}) {
  if (loading && !latest) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <AnswerColumnSkeleton key={i} />
        ))}
      </div>
    );
  }
  if (!latest) {
    return (
      <div className="rounded-2xl border border-dashed border-white/[0.08] bg-white/[0.02] p-10 text-center">
        <p className="font-mono text-[10px] tracking-[0.2em] uppercase text-ink-600">empty bench</p>
        <p className="mt-2 text-sm text-ink-400">
          Upload (or seed) a corpus, ask a question. Each retriever appears here, in parallel.
        </p>
      </div>
    );
  }

  const fastestId = pickFastest(latest.results);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
      {latest.results.map((r) => (
        <AnswerColumn key={r.method} result={r} fastest={r.method === fastestId} />
      ))}
    </div>
  );
}

function pickFastest(results: MethodResult[]): string | null {
  if (results.length === 0) return null;
  return results.reduce((a, b) => (b.latency_ms < a.latency_ms ? b : a)).method;
}
