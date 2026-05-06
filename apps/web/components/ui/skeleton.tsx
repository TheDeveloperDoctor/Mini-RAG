import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("rounded-md shimmer-bg animate-shimmer", className)} />;
}

export function AnswerColumnSkeleton() {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-panel-gradient p-5 space-y-4 shadow-panel">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-4 w-16" />
      </div>
      <Skeleton className="h-10 w-32" />
      <Skeleton className="h-1 w-full" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-5/6" />
      <div className="grid grid-cols-2 gap-2 pt-1">
        <Skeleton className="h-8" />
        <Skeleton className="h-8" />
        <Skeleton className="h-8" />
        <Skeleton className="h-8" />
      </div>
    </div>
  );
}
