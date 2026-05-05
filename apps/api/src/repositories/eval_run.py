"""Eval-run repository — persists harness output as JSON."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from src.core.db import db_conn


@dataclass(frozen=True)
class EvalRun:
    id: int
    corpus_size: int
    results: dict[str, Any]
    created_at: str


class EvalRunRepository:
    def create(self, *, corpus_size: int, results: dict[str, Any]) -> EvalRun:
        with db_conn() as conn:
            cur = conn.execute(
                "INSERT INTO eval_runs (corpus_size, results_json) VALUES (?, ?)",
                (corpus_size, json.dumps(results)),
            )
            run_id = int(cur.lastrowid or 0)
            row = conn.execute(
                "SELECT id, corpus_size, results_json, created_at FROM eval_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
        return self._row(row)

    def latest(self) -> EvalRun | None:
        with db_conn() as conn:
            row = conn.execute(
                "SELECT id, corpus_size, results_json, created_at FROM eval_runs ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return self._row(row) if row else None

    def history(self, limit: int = 20) -> list[EvalRun]:
        with db_conn() as conn:
            rows = conn.execute(
                "SELECT id, corpus_size, results_json, created_at FROM eval_runs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row(r) for r in rows]

    @staticmethod
    def _row(row: object) -> EvalRun:
        d = dict(row)  # type: ignore[arg-type]
        return EvalRun(
            id=int(d["id"]),
            corpus_size=int(d["corpus_size"]),
            results=json.loads(d["results_json"]),
            created_at=str(d["created_at"]),
        )
