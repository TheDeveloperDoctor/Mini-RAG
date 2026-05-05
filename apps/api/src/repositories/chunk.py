"""Chunk repository — stores text + raw float32 embedding bytes."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.core.db import db_conn


@dataclass(frozen=True)
class Chunk:
    id: int
    document_id: int
    ord: int
    text: str
    embedding: np.ndarray
    dim: int


def _vec_to_bytes(vec: np.ndarray) -> bytes:
    return np.ascontiguousarray(vec, dtype=np.float32).tobytes()


def _bytes_to_vec(data: bytes, dim: int) -> np.ndarray:
    return np.frombuffer(data, dtype=np.float32, count=dim).copy()


class ChunkRepository:
    def bulk_insert(
        self,
        *,
        document_id: int,
        items: list[tuple[int, str, np.ndarray]],
    ) -> int:
        if not items:
            return 0
        dim = int(items[0][2].shape[0])
        with db_conn() as conn:
            conn.executemany(
                """
                INSERT INTO chunks (document_id, ord, text, embedding, dim)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (document_id, ord_, text, _vec_to_bytes(vec), dim)
                    for ord_, text, vec in items
                ],
            )
        return len(items)

    def all_chunks(self) -> list[Chunk]:
        with db_conn() as conn:
            rows = conn.execute(
                "SELECT id, document_id, ord, text, embedding, dim FROM chunks ORDER BY id ASC"
            ).fetchall()
        return [self._row(r) for r in rows]

    def all_for_document(self, document_id: int) -> list[Chunk]:
        with db_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, document_id, ord, text, embedding, dim
                FROM chunks WHERE document_id = ? ORDER BY ord ASC
                """,
                (document_id,),
            ).fetchall()
        return [self._row(r) for r in rows]

    def get_many(self, ids: list[int]) -> list[Chunk]:
        if not ids:
            return []
        placeholders = ",".join(["?"] * len(ids))
        with db_conn() as conn:
            rows = conn.execute(
                f"SELECT id, document_id, ord, text, embedding, dim FROM chunks WHERE id IN ({placeholders})",
                tuple(ids),
            ).fetchall()
        by_id = {r["id"]: self._row(r) for r in rows}
        return [by_id[i] for i in ids if i in by_id]

    def count(self) -> int:
        with db_conn() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
        return int(row["n"])

    @staticmethod
    def _row(row: object) -> Chunk:
        d = dict(row)  # type: ignore[arg-type]
        return Chunk(
            id=int(d["id"]),
            document_id=int(d["document_id"]),
            ord=int(d["ord"]),
            text=str(d["text"]),
            embedding=_bytes_to_vec(d["embedding"], int(d["dim"])),
            dim=int(d["dim"]),
        )
