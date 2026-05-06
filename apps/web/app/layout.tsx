import type { Metadata } from "next";
import { Geist, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist",
  display: "swap",
  adjustFontFallback: false,
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
  adjustFontFallback: false,
});

export const metadata: Metadata = {
  title: "Mini RAG — Retriever Comparison Lab",
  description: "Naive vs FAISS Flat vs FAISS IVF vs BM25 vs Hybrid, head to head.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geist.variable} ${jetbrains.variable}`}>
      <body className="antialiased font-sans">{children}</body>
    </html>
  );
}
