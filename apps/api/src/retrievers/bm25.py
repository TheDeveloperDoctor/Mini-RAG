"""BM25 retriever — sparse keyword baseline via rank_bm25."""
from __future__ import annotations

import re
import sys
import time

import numpy as np

from src.repositories.chunk import Chunk
from src.retrievers.base import RetrievalHit, Retriever

_TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class BM25Retriever(Retriever):
    name = "bm25"

    def __init__(self) -> None:
        super().__init__()
        self._bm25: object | None = None
        self._ids: list[int] = []
        self._tokens: list[list[str]] = []

    def build(self, chunks: list[Chunk]) -> None:
        from rank_bm25 import BM25Okapi

        start = time.perf_counter()
        self._tokens = [_tokenize(c.text) for c in chunks]
        self._ids = [c.id for c in chunks]
        self._n = len(chunks)
        self._bm25 = BM25Okapi(self._tokens) if self._tokens else None
        self._size_bytes = sys.getsizeof(self._tokens) + sum(
            sys.getsizeof(t) for t in self._tokens
        )
        self._build_ms = (time.perf_counter() - start) * 1000.0

    def search(self, query_text: str, query_vec: np.ndarray, k: int) -> list[RetrievalHit]:
        if self._bm25 is None or self._n == 0:
            return []
        tokens = _tokenize(query_text)
        if not tokens:
            return []
        scores = np.asarray(self._bm25.get_scores(tokens), dtype=np.float32)  # type: ignore[attr-defined]
        top_n = min(k, scores.shape[0])
        top_idx = np.argpartition(-scores, top_n - 1)[:top_n]
        top_idx = top_idx[np.argsort(-scores[top_idx])]
        return [RetrievalHit(chunk_id=self._ids[i], score=float(scores[i])) for i in top_idx]
