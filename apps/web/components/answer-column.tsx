"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChunkInspector } from "@/components/chunk-inspector";
import { ErrorBoundary } from "@/components/error-boundary";
import { METHOD_COLORS, METHOD_LABELS, formatBytes, formatMs } from "@/lib/utils";
import type { MethodResult } from "@/lib/types";

interface Props {
  result: MethodResult;
}

export function AnswerColumn({ result }: Props) {
  const [showChunks, setShowChunks] = useState(false);
  const color = METHOD_COLORS[result.method] ?? "#94a3b8";
  const label = METHOD_LABELS[result.method] ?? result.method;

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
          <h4 className="text-sm font-medium text-ink-100">{label}</h4>
        </div>
        <Badge tone="accent" className="font-mono">
          {formatMs(result.latency_ms)}
        </Badge>
      </CardHeader>
      <CardBody className="flex-1 flex flex-col gap-3">
        <ErrorBoundary>
          <div className="text-sm text-ink-200 leading-relaxed min-h-[3rem]">
            {result.answer ?? <span className="italic text-ink-500">no answer requested</span>}
          </div>
        </ErrorBoundary>

        <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-ink-400">
          <Stat label="build" value={formatMs(result.build_ms)} />
          <Stat label="size" value={formatBytes(result.index_size_bytes)} />
          <Stat label="items" value={result.n_items.toLocaleString()} />
          <Stat label="hits" value={result.chunks.length.toString()} />
        </div>

        <button
          onClick={() => setShowChunks((s) => !s)}
          className="flex items-center gap-1 text-xs text-ink-400 hover:text-ink-200 transition-colors"
        >
          {showChunks ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          {showChunks ? "hide" : "show"} retrieved chunks
        </button>

        {showChunks && <ChunkInspector chunks={result.chunks} />}
      </CardBody>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-ink-800/40 px-2 py-1.5">
      <div className="text-ink-500 uppercase tracking-wider text-[9px]">{label}</div>
      <div className="text-ink-200">{value}</div>
    </div>
  );
}
