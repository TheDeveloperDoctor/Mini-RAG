"""Eval harness — measure recall@k, MRR, and latency for every retriever.

The eval is self-contained: it loads `corpus.md` + `gold.jsonl`, builds
retrievers in memory, and never touches the runtime SQLite database. That keeps
runs deterministic and reproducible regardless of what's been uploaded.

Run as: `python -m src.eval.harness`
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from src.chunking import chunk_text
from src.core.config import get_settings
from src.core.logger import Logger, get_logger
from src.embeddings import get_embedder
from src.repositories.chunk import Chunk
from src.retrievers import RETRIEVER_NAMES, build_all

logger = get_logger(__name__)

_HERE = Path(__file__).parent
_CORPUS_PATH = _HERE / "corpus.md"
_GOLD_PATH = _HERE / "gold.jsonl"
_RESULTS_DIR = Path(__file__).resolve().parents[3] / "eval_results"


def _load_corpus_chunks() -> list[Chunk]:
    text = _CORPUS_PATH.read_text(encoding="utf-8")
    settings = get_settings()
    pieces = chunk_text(text, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    embedder = get_embedder()
    vectors = embedder.encode([p.text for p in pieces])
    return [
        Chunk(
            id=i + 1,  # synthetic ids — eval doesn't touch the real DB
            document_id=0,
            ord=p.ord,
            text=p.text,
            embedding=vectors[i],
            dim=int(vectors[i].shape[0]),
        )
        for i, p in enumerate(pieces)
    ]


def _load_gold() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with _GOLD_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _gold_chunk_ids(chunks: list[Chunk], substrings: list[str]) -> set[int]:
    targets = [s.lower() for s in substrings]
    return {c.id for c in chunks if any(t in c.text.lower() for t in targets)}


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def run_eval() -> dict[str, Any]:
    Logger.initialize()
    chunks = _load_corpus_chunks()
    gold = _load_gold()
    embedder = get_embedder()

    retrievers = build_all(chunks, list(RETRIEVER_NAMES))

    # Pre-encode every gold question once — no point paying that cost per retriever.
    queries = [(g["question"], embedder.encode_one(g["question"])) for g in gold]
    gold_sets = [_gold_chunk_ids(chunks, g["relevant_substrings"]) for g in gold]

    summary: list[dict[str, Any]] = []
    for name, retriever in retrievers.items():
        recall5: list[float] = []
        recall10: list[float] = []
        rr: list[float] = []
        latencies: list[float] = []

        for (question, vec), gold_ids in zip(queries, gold_sets):
            if not gold_ids:
                continue
            start = time.perf_counter()
            hits = retriever.search(question, vec, 10)
            latencies.append((time.perf_counter() - start) * 1000.0)

            top_ids = [h.chunk_id for h in hits]
            recall5.append(_recall_at_k(top_ids, gold_ids, 5))
            recall10.append(_recall_at_k(top_ids, gold_ids, 10))
            rr.append(_reciprocal_rank(top_ids, gold_ids))

        summary.append(
            {
                "method": name,
                "recall_at_5": round(statistics.mean(recall5) if recall5 else 0.0, 4),
                "recall_at_10": round(statistics.mean(recall10) if recall10 else 0.0, 4),
                "mrr": round(statistics.mean(rr) if rr else 0.0, 4),
                "p50_latency_ms": round(_percentile(latencies, 50), 3),
                "p95_latency_ms": round(_percentile(latencies, 95), 3),
                "build_ms": round(retriever.build_ms, 3),
                "index_size_bytes": int(retriever.size_bytes),
            }
        )
    return {"corpus_size": len(chunks), "methods": summary}


def _recall_at_k(top_ids: list[int], gold: set[int], k: int) -> float:
    if not gold:
        return 0.0
    hits = sum(1 for cid in top_ids[:k] if cid in gold)
    return hits / len(gold)


def _reciprocal_rank(top_ids: list[int], gold: set[int]) -> float:
    for i, cid in enumerate(top_ids, start=1):
        if cid in gold:
            return 1.0 / i
    return 0.0


def _print_table(rows: list[dict[str, Any]]) -> None:
    headers = ["method", "recall@5", "recall@10", "mrr", "p50_ms", "p95_ms", "build_ms", "size_kb"]
    print(" | ".join(f"{h:>11}" for h in headers))
    print("-" * (len(headers) * 14))
    for r in rows:
        print(
            " | ".join(
                [
                    f"{r['method']:>11}",
                    f"{r['recall_at_5']:>11.3f}",
                    f"{r['recall_at_10']:>11.3f}",
                    f"{r['mrr']:>11.3f}",
                    f"{r['p50_latency_ms']:>11.3f}",
                    f"{r['p95_latency_ms']:>11.3f}",
                    f"{r['build_ms']:>11.2f}",
                    f"{r['index_size_bytes'] / 1024:>11.1f}",
                ]
            )
        )


def main() -> int:
    result = run_eval()
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _RESULTS_DIR / f"eval_{int(time.time())}.json"
    out_path.write_text(json.dumps(result, indent=2))
    _print_table(result["methods"])
    print(f"\ncorpus_size={result['corpus_size']}  wrote {out_path.relative_to(_RESULTS_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
