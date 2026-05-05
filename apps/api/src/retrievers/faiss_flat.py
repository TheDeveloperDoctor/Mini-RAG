"""FAISS IndexFlatIP — exact, SIMD-accelerated inner product."""
from __future__ import annotations

import time

import numpy as np

from src.repositories.chunk import Chunk
from src.retrievers.base import RetrievalHit, Retriever


class FAISSFlatRetriever(Retriever):
    name = "faiss_flat"

    def __init__(self) -> None:
        super().__init__()
        self._index: object | None = None
        self._ids: list[int] = []

    def build(self, chunks: list[Chunk]) -> None:
        import faiss  # heavy import deferred

        start = time.perf_counter()
        if not chunks:
            self._index = None
            self._ids = []
            self._n = 0
            self._size_bytes = 0
            self._build_ms = (time.perf_counter() - start) * 1000.0
            return

        dim = int(chunks[0].embedding.shape[0])
        matrix = np.vstack([c.embedding for c in chunks]).astype(np.float32, copy=False)
        index = faiss.IndexFlatIP(dim)
        index.add(matrix)

        self._index = index
        self._ids = [c.id for c in chunks]
        self._n = len(chunks)
        self._size_bytes = int(matrix.nbytes)
        self._build_ms = (time.perf_counter() - start) * 1000.0

    def search(self, query_text: str, query_vec: np.ndarray, k: int) -> list[RetrievalHit]:
        if self._index is None or self._n == 0:
            return []
        q = query_vec.astype(np.float32, copy=False).reshape(1, -1)
        scores, idx = self._index.search(q, min(k, self._n))  # type: ignore[attr-defined]
        return [
            RetrievalHit(chunk_id=self._ids[int(i)], score=float(s))
            for s, i in zip(scores[0], idx[0])
            if int(i) >= 0
        ]
