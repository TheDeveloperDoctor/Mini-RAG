import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatMs(value: number): string {
  if (value < 1) return `${(value * 1000).toFixed(0)}µs`;
  if (value < 100) return `${value.toFixed(2)}ms`;
  return `${value.toFixed(0)}ms`;
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
}

export const METHOD_COLORS: Record<string, string> = {
  naive: "#FBBF24",
  faiss_flat: "#6EE7B7",
  faiss_ivf: "#A78BFA",
  bm25: "#34D399",
  hybrid: "#F472B6",
};

export const METHOD_LABELS: Record<string, string> = {
  naive: "Naive cosine",
  faiss_flat: "FAISS Flat",
  faiss_ivf: "FAISS IVF",
  bm25: "BM25",
  hybrid: "Hybrid (RRF)",
};
