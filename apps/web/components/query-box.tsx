"use client";

import { useState, type FormEvent } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/input";
import { Card, CardBody } from "@/components/ui/card";

interface Props {
  loading: boolean;
  onSubmit: (q: string, topK: number, synthesize: boolean) => void;
}

export function QueryBox({ loading, onSubmit }: Props) {
  const [question, setQuestion] = useState("Who pioneered the smallpox vaccine and when?");
  const [topK, setTopK] = useState(5);
  const [synthesize, setSynthesize] = useState(true);

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;
    onSubmit(question.trim(), topK, synthesize);
  }

  return (
    <Card glow>
      <CardBody className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-[10px] tracking-[0.2em] text-mint">02</span>
            <h3 className="text-[15px] font-semibold text-ink-100">Query</h3>
          </div>
          <span className="font-mono text-[10px] tracking-[0.16em] uppercase text-ink-600">
            5 retrievers · parallel
          </span>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about the corpus…"
            disabled={loading}
            rows={2}
          />
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div className="flex items-center gap-5 font-mono text-xs text-ink-400">
              <label className="flex items-center gap-2">
                <span className="text-ink-600">top_k</span>
                <input
                  type="number"
                  min={1}
                  max={20}
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="h-7 w-14 rounded-md border border-white/[0.08] bg-black/40 px-2 text-mint focus:border-mint/40 focus:outline-none disabled:opacity-50"
                  disabled={loading}
                />
              </label>
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={synthesize}
                  onChange={(e) => setSynthesize(e.target.checked)}
                  className="accent-mint"
                  disabled={loading}
                />
                <span className="text-ink-600">synthesize</span>
                <span className={synthesize ? "text-mint font-semibold" : "text-ink-500"}>
                  {synthesize ? "ON" : "OFF"}
                </span>
              </label>
              <span className="hidden sm:inline">
                <span className="text-ink-600">parallel</span>{" "}
                <span className="text-amber font-semibold">5×</span>
              </span>
            </div>

            <Button type="submit" size="md" disabled={loading || !question.trim()}>
              {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <span aria-hidden>▸</span>}
              {loading ? "Running…" : "Run query"}
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  );
}
