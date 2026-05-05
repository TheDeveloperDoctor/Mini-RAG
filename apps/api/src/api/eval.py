"""Eval routes — kick off a run, fetch the latest, list history."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.deps import get_eval_repo
from src.api.schemas import EvalMethodMetrics, EvalRunOut
from src.eval.harness import run_eval
from src.repositories.eval_run import EvalRun, EvalRunRepository

router = APIRouter(prefix="/v1/eval", tags=["eval"])


@router.post("/run", response_model=EvalRunOut)
def trigger_run(repo: EvalRunRepository = Depends(get_eval_repo)) -> EvalRunOut:
    result = run_eval()
    record = repo.create(
        corpus_size=int(result.get("corpus_size", 0)),
        results={"methods": result.get("methods", [])},
    )
    return _to_out(record)


@router.get("/latest", response_model=EvalRunOut | None)
def latest(repo: EvalRunRepository = Depends(get_eval_repo)) -> EvalRunOut | None:
    record = repo.latest()
    return _to_out(record) if record else None


@router.get("/history", response_model=list[EvalRunOut])
def history(repo: EvalRunRepository = Depends(get_eval_repo)) -> list[EvalRunOut]:
    return [_to_out(r) for r in repo.history()]


def _to_out(record: EvalRun) -> EvalRunOut:
    methods = [EvalMethodMetrics(**m) for m in record.results.get("methods", [])]
    return EvalRunOut(
        id=record.id,
        corpus_size=record.corpus_size,
        created_at=record.created_at,
        methods=methods,
    )
