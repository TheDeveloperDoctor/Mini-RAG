"use client";

import { useState, type FormEvent } from "react";
import { Send, Loader2 } from "lucide-react";
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
    <Card>
      <CardBody>
        <form onSubmit={submit} className="space-y-3">
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about the corpus…"
            disabled={loading}
          />
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div className="flex items-center gap-3 text-xs text-ink-300">
              <label className="flex items-center gap-2">
                top_k
                <input
                  type="number"
                  min={1}
                  max={20}
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="h-7 w-16 rounded border border-ink-700 bg-ink-900 px-2 font-mono text-ink-100"
                  disabled={loading}
                />
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={synthesize}
                  onChange={(e) => setSynthesize(e.target.checked)}
                  className="accent-accent"
                  disabled={loading}
                />
                synthesize answer
              </label>
            </div>

            <Button type="submit" size="md" disabled={loading || !question.trim()}>
              {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Send className="h-3 w-3" />}
              {loading ? "Running…" : "Run query"}
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  );
}
