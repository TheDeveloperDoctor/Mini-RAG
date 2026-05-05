"""Recursive character chunker that respects natural boundaries.

Splits along the longest separator that fits, falling back to shorter ones.
Output chunks include configurable overlap to preserve context across breaks.
"""
from __future__ import annotations

from dataclasses import dataclass

_DEFAULT_SEPARATORS: tuple[str, ...] = ("\n\n", "\n", ". ", " ", "")


@dataclass(frozen=True)
class Chunk:
    text: str
    ord: int


class RecursiveChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 80,
        separators: tuple[str, ...] = _DEFAULT_SEPARATORS,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be in [0, chunk_size)")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators

    def split(self, text: str) -> list[Chunk]:
        cleaned = text.strip()
        if not cleaned:
            return []
        pieces = self._split_recursive(cleaned, self.separators)
        merged = self._merge(pieces)
        return [Chunk(text=t, ord=i) for i, t in enumerate(merged)]

    def _split_recursive(self, text: str, separators: tuple[str, ...]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        separator = separators[0] if separators else ""
        rest = separators[1:] if len(separators) > 1 else ()

        if separator == "":
            return self._hard_split(text)

        if separator not in text:
            return self._split_recursive(text, rest)

        out: list[str] = []
        for piece in text.split(separator):
            if not piece:
                continue
            piece_with_sep = piece + (separator if separator.strip() else "")
            if len(piece_with_sep) <= self.chunk_size:
                out.append(piece_with_sep)
            else:
                out.extend(self._split_recursive(piece_with_sep, rest))
        return out

    def _hard_split(self, text: str) -> list[str]:
        return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

    def _merge(self, pieces: list[str]) -> list[str]:
        chunks: list[str] = []
        buffer = ""
        for piece in pieces:
            if not piece.strip():
                continue
            if len(buffer) + len(piece) <= self.chunk_size:
                buffer += piece
                continue
            if buffer:
                chunks.append(buffer.strip())
            buffer = self._with_overlap(chunks, piece)
        if buffer.strip():
            chunks.append(buffer.strip())
        return chunks

    def _with_overlap(self, chunks: list[str], next_piece: str) -> str:
        if not chunks or self.chunk_overlap == 0:
            return next_piece
        tail = chunks[-1][-self.chunk_overlap :]
        return tail + next_piece


def chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    return RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap).split(text)
