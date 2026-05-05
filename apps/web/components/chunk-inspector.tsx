"use client";

import type { RetrievedChunk } from "@/lib/types";

interface Props {
  chunks: RetrievedChunk[];
}

export function ChunkInspector({ chunks }: Props) {
  if (chunks.length === 0) {
    return <p className="text-xs italic text-ink-500">no chunks returned</p>;
  }
  return (
    <ol className="space-y-2 max-h-72 overflow-y-auto scroll-thin">
      {chunks.map((chunk, i) => (
        <li
          key={chunk.chunk_id}
          className="rounded-md border border-ink-800 bg-ink-900/40 p-2.5 text-xs text-ink-300"
        >
          <div className="flex items-center justify-between text-[10px] font-mono text-ink-500 mb-1">
            <span>
              #{i + 1} · chunk {chunk.chunk_id} · ord {chunk.ord}
            </span>
            <span className="text-accent">score {chunk.score.toFixed(3)}</span>
          </div>
          <div className="line-clamp-4 leading-relaxed">{chunk.text}</div>
        </li>
      ))}
    </ol>
  );
}
