import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mini RAG — Retriever Comparison Lab",
  description: "Naive vs FAISS Flat vs FAISS IVF vs BM25 vs Hybrid, head to head.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <header className="border-b border-ink-800/70 bg-ink-950/80 backdrop-blur sticky top-0 z-10">
          <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 text-ink-100 font-semibold">
              <span className="inline-block h-2 w-2 rounded-full bg-accent shadow-[0_0_12px_rgba(34,211,238,0.7)]" />
              Mini RAG
              <span className="ml-2 text-xs uppercase tracking-wider text-ink-400">
                comparison lab
              </span>
            </a>
            <nav className="text-sm text-ink-300 flex gap-6">
              <a href="/" className="hover:text-ink-100">
                Lab
              </a>
              <a href="/eval" className="hover:text-ink-100">
                Eval
              </a>
              <a
                href="https://github.com"
                className="hover:text-ink-100"
                rel="noreferrer noopener"
                target="_blank"
              >
                GitHub
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        <footer className="border-t border-ink-800/70 mt-16">
          <div className="mx-auto max-w-7xl px-6 py-6 text-xs text-ink-500 flex justify-between">
            <span>Local embeddings · BAAI/bge-small-en-v1.5</span>
            <span>Built to be measured, not impressive.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
