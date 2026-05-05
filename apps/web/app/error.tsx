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
    <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-8 text-center max-w-xl mx-auto mt-12">
      <AlertTriangle className="mx-auto h-8 w-8 text-amber-300" />
      <h2 className="mt-4 text-lg font-semibold text-amber-100">Something broke.</h2>
      <p className="mt-2 text-sm text-amber-200/80">{error.message}</p>
      {error.digest && (
        <p className="mt-1 text-xs font-mono text-amber-300/60">digest: {error.digest}</p>
      )}
      <Button onClick={reset} variant="secondary" className="mt-5">
        <RotateCw className="h-3 w-3" />
        Try again
      </Button>
    </div>
  );
}
