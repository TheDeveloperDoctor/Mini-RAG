"""Naive retriever — pure numpy cosine similarity, O(n) per query.

Used as the truthful, slow baseline. Its top-k is also our ground truth for
recall@k of the approximate retrievers.
"""
from __future__ import annotations

import time

import numpy as np

from src.repositories.chunk import Chunk
from src.retrievers.base import RetrievalHit, Retriever


class NaiveRetriever(Retriever):
    name = "naive"

    def __init__(self) -> None:
        super().__init__()
        self._matrix: np.ndarray | None = None
        self._ids: list[int] = []

    def build(self, chunks: list[Chunk]) -> None:
        start = time.perf_counter()
        if not chunks:
            self._matrix = np.zeros((0, 0), dtype=np.float32)
            self._ids = []
            self._n = 0
            self._size_bytes = 0
        else:
            self._matrix = np.vstack([c.embedding for c in chunks]).astype(np.float32, copy=False)
            self._ids = [c.id for c in chunks]
            self._n = len(chunks)
            self._size_bytes = int(self._matrix.nbytes)
        self._build_ms = (time.perf_counter() - start) * 1000.0

    def search(self, query_text: str, query_vec: np.ndarray, k: int) -> list[RetrievalHit]:
        if self._matrix is None or self._matrix.size == 0:
            return []
        scores = self._matrix @ query_vec.astype(np.float32, copy=False)
        top_n = min(k, scores.shape[0])
        top_idx = np.argpartition(-scores, top_n - 1)[:top_n]
        top_idx = top_idx[np.argsort(-scores[top_idx])]
        return [RetrievalHit(chunk_id=self._ids[i], score=float(scores[i])) for i in top_idx]
