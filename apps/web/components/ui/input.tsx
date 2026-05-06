"use client";

import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const baseInput =
  "w-full rounded-xl border border-white/[0.08] bg-black/40 text-ink-100 placeholder:text-ink-500 transition-shadow focus:border-mint/40 focus:outline-none focus:shadow-[inset_0_0_24px_rgba(110,231,183,0.06),0_0_0_1px_rgba(110,231,183,0.25)] disabled:cursor-not-allowed disabled:opacity-50";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input ref={ref} className={cn(baseInput, "h-10 px-4 text-sm", className)} {...props} />
  ),
);
Input.displayName = "Input";

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(baseInput, "min-h-[88px] py-3 px-4 text-base leading-relaxed", className)}
      {...props}
    />
  ),
);
Textarea.displayName = "Textarea";
