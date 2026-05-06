"use client";

import { AlertTriangle, RotateCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="rounded-2xl border border-amber/30 bg-amber/[0.05] p-8 text-center max-w-xl mx-auto mt-12 shadow-panel">
      <AlertTriangle className="mx-auto h-8 w-8 text-amber" />
      <h2 className="mt-4 text-lg font-semibold text-ink-100">Something broke.</h2>
      <p className="mt-2 text-sm text-amber/90">{error.message}</p>
      {error.digest && (
        <p className="mt-1 font-mono text-xs text-amber/60">digest: {error.digest}</p>
      )}
      <Button onClick={reset} variant="secondary" className="mt-6">
        <RotateCw className="h-3.5 w-3.5" />
        Try again
      </Button>
    </div>
  );
}
