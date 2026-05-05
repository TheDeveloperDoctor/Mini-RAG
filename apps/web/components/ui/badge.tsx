"use client";

import { forwardRef, type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "neutral" | "accent" | "warn";
}

const toneClasses: Record<NonNullable<BadgeProps["tone"]>, string> = {
  neutral: "bg-ink-800 text-ink-300 border-ink-700",
  accent: "bg-accent/10 text-accent border-accent/30",
  warn: "bg-amber-500/10 text-amber-300 border-amber-500/30",
};

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, tone = "neutral", ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-mono uppercase tracking-wider",
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  ),
);
Badge.displayName = "Badge";
