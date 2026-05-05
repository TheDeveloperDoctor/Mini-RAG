"""FAISS IndexIVFFlat — approximate ANN with tunable nlist / nprobe.

For small corpora (< ~256 vectors) IVF can't train enough centroids. In that
case we transparently fall back to Flat so the comparison stays honest rather
than failing.
"""
from __future__ import annotations

import math
import time

import numpy as np

from src.core.logger import get_logger
from src.repositories.chunk import Chunk
from src.retrievers.base import RetrievalHit, Retriever

logger = get_logger(__name__)

_MIN_FOR_IVF = 256


class FAISSIVFRetriever(Retriever):
    name = "faiss_ivf"

    def __init__(self, nlist: int | None = None, nprobe: int = 8) -> None:
        super().__init__()
        self._index: object | None = None
        self._ids: list[int] = []
        self._nlist_override = nlist
        self._nprobe = nprobe
        self._effective_nlist = 0
        self._fell_back = False

    def build(self, chunks: list[Chunk]) -> None:
        import faiss

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
        n = matrix.shape[0]

        if n < _MIN_FOR_IVF:
            self._fell_back = True
            index = faiss.IndexFlatIP(dim)
            index.add(matrix)
            self._effective_nlist = 0
        else:
            self._fell_back = False
            nlist = self._nlist_override or max(8, int(math.sqrt(n)))
            quantizer = faiss.IndexFlatIP(dim)
            index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
            index.train(matrix)
            index.add(matrix)
            index.nprobe = self._nprobe
            self._effective_nlist = nlist

        self._index = index
        self._ids = [c.id for c in chunks]
        self._n = n
        self._size_bytes = int(matrix.nbytes)
        self._build_ms = (time.perf_counter() - start) * 1000.0

        logger.debug(
            "ivf_built",
            extra={
                "n": n,
                "fell_back": self._fell_back,
                "nlist": self._effective_nlist,
                "nprobe": self._nprobe,
            },
        )

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

    @property
    def info(self) -> dict[str, int | bool]:
        return {
            "nlist": self._effective_nlist,
            "nprobe": self._nprobe,
            "fell_back_to_flat": self._fell_back,
        }
