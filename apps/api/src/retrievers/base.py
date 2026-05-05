"""Retriever protocol — every strategy implements the same shape.

Indices are built once per corpus and queried many times. The contract is
intentionally minimal: build, search, and a few self-reported stats so the
benchmark UI can render apples-to-apples comparisons.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from src.repositories.chunk import Chunk


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: int
    score: float


class Retriever(ABC):
    name: str = "base"

    def __init__(self) -> None:
        self._build_ms: float = 0.0
        self._size_bytes: int = 0
        self._n: int = 0

    @abstractmethod
    def build(self, chunks: list[Chunk]) -> None:
        """Build the index. Must populate _build_ms, _size_bytes, _n."""

    @abstractmethod
    def search(self, query_text: str, query_vec: np.ndarray, k: int) -> list[RetrievalHit]:
        """Return up to k hits, highest score first."""

    @property
    def build_ms(self) -> float:
        return self._build_ms

    @property
    def size_bytes(self) -> int:
        return self._size_bytes

    @property
    def n_items(self) -> int:
        return self._n
