"use client";

import { forwardRef, type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Tone = "neutral" | "accent" | "warn" | "amber" | "violet" | "rose";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

const toneClasses: Record<Tone, string> = {
  neutral: "bg-white/[0.04] text-ink-300 border-white/[0.08]",
  accent: "bg-mint/10 text-mint border-mint/30",
  warn: "bg-amber/10 text-amber border-amber/30",
  amber: "bg-amber/10 text-amber border-amber/30",
  violet: "bg-violet/10 text-violet border-violet/30",
  rose: "bg-rose/10 text-rose border-rose/30",
};

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, tone = "neutral", ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[10px] font-mono uppercase tracking-[0.14em]",
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  ),
);
Badge.displayName = "Badge";
