"use client";

import { useState, type ChangeEvent } from "react";
import { Upload, FileText, Loader2, AlertTriangle } from "lucide-react";
import { Card, CardBody } from "@/components/ui/card";
import { documentsRepo } from "@/lib/api/repositories/documents";
import { ApiError } from "@/lib/api/client";
import { formatBytes } from "@/lib/utils";
import type { DocumentDTO } from "@/lib/types";

interface Props {
  documents: DocumentDTO[];
  onUploaded: () => void;
}

export function UploadPanel({ documents, onUploaded }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      await documentsRepo.upload(file);
      onUploaded();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Upload failed";
      setError(msg);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <Card>
      <CardBody className="space-y-4">
        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-[10px] tracking-[0.2em] text-mint">01</span>
            <h3 className="text-[15px] font-semibold text-ink-100">Corpus</h3>
          </div>
          <span className="font-mono text-[10px] tracking-[0.16em] uppercase text-ink-600">
            {documents.length} {documents.length === 1 ? "doc" : "docs"}
          </span>
        </div>

        <p className="text-xs text-ink-400 leading-relaxed">
          Upload <code className="font-mono text-ink-200">.txt</code> or{" "}
          <code className="font-mono text-ink-200">.md</code>, or run{" "}
          <code className="font-mono text-mint/90">make seed</code> for the starter corpus.
        </p>

        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-amber/30 bg-amber/5 px-3 py-2 text-xs text-amber">
            <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {documents.length === 0 ? (
          <p className="text-xs text-ink-500 italic">No documents yet.</p>
        ) : (
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="rounded-xl border border-white/[0.04] bg-white/[0.02] px-3 py-2.5 transition-colors hover:bg-white/[0.04]"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText className="h-3.5 w-3.5 text-mint/70 shrink-0" />
                    <span className="font-mono text-xs text-ink-200 truncate">{doc.name}</span>
                  </div>
                  <span className="font-mono text-[10px] text-ink-500 shrink-0">
                    {formatBytes(doc.byte_size)}
                  </span>
                </div>
                <div className="mt-1 ml-5 font-mono text-[10px] text-ink-600">
                  uploaded {doc.created_at.slice(0, 10)}
                </div>
              </li>
            ))}
          </ul>
        )}

        <label
          className={
            "flex items-center justify-center gap-2 cursor-pointer rounded-full px-4 py-2 text-xs font-medium border border-white/[0.08] bg-white/[0.04] text-ink-100 hover:bg-white/[0.08] transition-colors " +
            (uploading ? "opacity-50 cursor-not-allowed" : "")
          }
        >
          <input
            type="file"
            accept=".txt,.md,.markdown"
            onChange={handleFile}
            className="hidden"
            disabled={uploading}
          />
          {uploading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Upload className="h-3.5 w-3.5" />}
          {uploading ? "Uploading…" : "Upload .txt / .md"}
        </label>
      </CardBody>
    </Card>
  );
}
