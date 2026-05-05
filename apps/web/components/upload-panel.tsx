"use client";

import { useState, type ChangeEvent } from "react";
import { Upload, FileText, Loader2 } from "lucide-react";
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
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-ink-100">Corpus</h3>
            <p className="text-xs text-ink-400 mt-0.5">
              Upload .txt or .md, or run <code className="text-ink-200">make seed</code> for a starter corpus.
            </p>
          </div>
          <label
            className={
              "inline-flex items-center justify-center gap-2 rounded-md font-medium h-8 px-3 text-xs cursor-pointer " +
              "bg-accent text-ink-950 hover:bg-accent-dim shadow-[0_0_18px_-6px_rgba(34,211,238,0.7)] " +
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
            {uploading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Upload className="h-3 w-3" />}
            {uploading ? "Uploading…" : "Upload"}
          </label>
        </div>

        {error && <p className="text-xs text-amber-300">{error}</p>}

        {documents.length === 0 ? (
          <p className="text-xs text-ink-500 italic">No documents yet.</p>
        ) : (
          <ul className="space-y-1">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="flex items-center justify-between rounded-md bg-ink-800/40 px-3 py-2 text-xs text-ink-200"
              >
                <span className="flex items-center gap-2 truncate">
                  <FileText className="h-3 w-3 text-ink-400 shrink-0" />
                  <span className="truncate">{doc.name}</span>
                </span>
                <span className="text-ink-500 font-mono shrink-0 ml-3">
                  {formatBytes(doc.byte_size)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}
