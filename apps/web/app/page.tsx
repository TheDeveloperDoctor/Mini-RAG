"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { UploadPanel } from "@/components/upload-panel";
import { QueryBox } from "@/components/query-box";
import { AnswerColumn } from "@/components/answer-column";
import { LatencyChart } from "@/components/latency-chart";
import { ErrorBoundary } from "@/components/error-boundary";
import { documentsRepo } from "@/lib/api/repositories/documents";
import { queryRepo } from "@/lib/api/repositories/query";
import { ApiError } from "@/lib/api/client";
import type { DocumentDTO, QueryResponse } from "@/lib/types";

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
    <div className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-ink-100">Retriever Comparison Lab</h1>
        <p className="text-sm text-ink-400 mt-1 max-w-3xl">
          One question, four retrievers, side by side. Look at the latency badges and the chunk
          scores — the cost of each retrieval choice is visible. <span className="text-ink-300">No vibes.</span>
        </p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
        <ErrorBoundary>
          <UploadPanel documents={documents} onUploaded={refreshDocuments} />
        </ErrorBoundary>
        <ErrorBoundary>
          <QueryBox loading={loading} onSubmit={handleQuery} />
        </ErrorBoundary>
      </div>

      {error && (
        <div className="rounded-md border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
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
      <div className="rounded-xl border border-ink-800 bg-ink-900/40 p-8 text-center text-sm text-ink-400">
        Running query through every retriever…
      </div>
    );
  }
  if (!latest) {
    return (
      <div className="rounded-xl border border-dashed border-ink-800 bg-ink-900/30 p-8 text-center text-sm text-ink-500">
        Upload (or seed) a corpus, ask a question. Each retriever will appear here side-by-side.
      </div>
    );
  }
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
      {latest.results.map((r) => (
        <AnswerColumn key={r.method} result={r} />
      ))}
    </div>
  );
}
