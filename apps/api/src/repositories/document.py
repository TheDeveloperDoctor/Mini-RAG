"""Document repository — encapsulates SQL behind a typed interface."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.db import db_conn


@dataclass(frozen=True)
class Document:
    id: int
    name: str
    byte_size: int
    created_at: str


class DocumentRepository:
    def create(self, *, name: str, byte_size: int) -> Document:
        with db_conn() as conn:
            cur = conn.execute(
                "INSERT INTO documents (name, byte_size) VALUES (?, ?)",
                (name, byte_size),
            )
            doc_id = int(cur.lastrowid or 0)
            row = conn.execute(
                "SELECT id, name, byte_size, created_at FROM documents WHERE id = ?",
                (doc_id,),
            ).fetchone()
        return Document(**dict(row))

    def list_all(self) -> list[Document]:
        with db_conn() as conn:
            rows = conn.execute(
                "SELECT id, name, byte_size, created_at FROM documents ORDER BY id DESC"
            ).fetchall()
        return [Document(**dict(r)) for r in rows]

    def get(self, doc_id: int) -> Document | None:
        with db_conn() as conn:
            row = conn.execute(
                "SELECT id, name, byte_size, created_at FROM documents WHERE id = ?",
                (doc_id,),
            ).fetchone()
        return Document(**dict(row)) if row else None

    def delete(self, doc_id: int) -> None:
        with db_conn() as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
