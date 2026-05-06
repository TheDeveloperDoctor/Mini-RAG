"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { ChunkInspector } from "@/components/chunk-inspector";
import { ErrorBoundary } from "@/components/error-boundary";
import { METHOD_COLORS, METHOD_LABELS, formatBytes, formatMs } from "@/lib/utils";
import type { MethodResult } from "@/lib/types";

interface Props {
  result: MethodResult;
  fastest?: boolean;
}

export function AnswerColumn({ result, fastest }: Props) {
  const [showChunks, setShowChunks] = useState(false);
  const hue = METHOD_COLORS[result.method] ?? "#A3B0C7";
  const label = METHOD_LABELS[result.method] ?? result.method;

  return (
    <div
      className="relative h-full flex flex-col rounded-2xl border border-white/[0.06] bg-panel-gradient shadow-panel overflow-hidden"
    >
      <div
        aria-hidden
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle at 0% 0%, ${hue}22 0%, transparent 50%)`,
        }}
      />

      <div className="relative p-5 flex flex-col gap-4 flex-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span
              className="h-2 w-2 rounded-full"
              style={{ background: hue, boxShadow: `0 0 12px ${hue}99` }}
            />
            <h4 className="text-[13px] font-semibold text-ink-100 tracking-tight">{label}</h4>
          </div>
          {fastest && (
            <span className="font-mono text-[9px] tracking-[0.2em] uppercase text-mint">
              fastest
            </span>
          )}
        </div>

        <div className="font-mono">
          <div className="flex items-baseline gap-1.5">
            <span
              className="text-[34px] font-bold leading-none tracking-tight tabular-nums"
              style={{ color: hue, textShadow: `0 0 24px ${hue}66` }}
            >
              {result.latency_ms.toFixed(2)}
            </span>
            <span className="text-xs text-ink-400">ms</span>
          </div>
          <Meter value={result.latency_ms} max={200} hue={hue} />
        </div>

        <ErrorBoundary>
          <div className="text-sm text-ink-200 leading-relaxed min-h-[3rem]">
            {result.answer ?? <span className="italic text-ink-500">no answer requested</span>}
          </div>
        </ErrorBoundary>

        <div className="grid grid-cols-2 gap-1.5 font-mono text-[11px]">
          <Stat label="build" value={formatMs(result.build_ms)} />
          <Stat label="size" value={formatBytes(result.index_size_bytes)} />
          <Stat label="items" value={result.n_items.toLocaleString()} />
          <Stat label="hits" value={result.chunks.length.toString()} />
        </div>

        <button
          onClick={() => setShowChunks((s) => !s)}
          className="flex items-center gap-1 font-mono text-[11px] text-ink-400 hover:text-ink-200 transition-colors w-fit"
        >
          {showChunks ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          {showChunks ? "hide" : "show"} retrieved chunks
        </button>

        {showChunks && <ChunkInspector chunks={result.chunks} hue={hue} />}
      </div>
    </div>
  );
}

function Meter({ value, max, hue }: { value: number; max: number; hue: string }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="mt-2 h-1 rounded-full bg-white/[0.06] overflow-hidden">
      <div
        className="h-full"
        style={{ width: `${pct}%`, background: hue, boxShadow: `0 0 12px ${hue}` }}
      />
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-white/[0.04] bg-white/[0.025] px-2.5 py-1.5">
      <span className="text-ink-600 uppercase tracking-[0.1em] text-[9px]">{label}</span>
      <span className="text-ink-100 tabular-nums">{value}</span>
    </div>
  );
}
