"use client";

import type { RetrievedChunk } from "@/lib/types";

interface Props {
  chunks: RetrievedChunk[];
  hue?: string;
}

export function ChunkInspector({ chunks, hue = "#6EE7B7" }: Props) {
  if (chunks.length === 0) {
    return <p className="font-mono text-[11px] italic text-ink-500">no chunks returned</p>;
  }
  return (
    <ol className="space-y-2 max-h-72 overflow-y-auto scroll-thin pr-1">
      {chunks.map((chunk, i) => (
        <li
          key={chunk.chunk_id}
          className="rounded-lg border border-white/[0.04] bg-white/[0.025] p-3 text-xs text-ink-200"
          style={{ borderLeft: `2px solid ${hue}` }}
        >
          <div className="flex items-center justify-between font-mono text-[10px] text-ink-500 mb-1.5">
            <span>
              #{String(i + 1).padStart(2, "0")} · doc {chunk.document_id} · ord {chunk.ord}
            </span>
            <span style={{ color: hue, fontWeight: 600 }}>score {chunk.score.toFixed(3)}</span>
          </div>
          <div className="line-clamp-4 leading-relaxed">{chunk.text}</div>
        </li>
      ))}
    </ol>
  );
}
