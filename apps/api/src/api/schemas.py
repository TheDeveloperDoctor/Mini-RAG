"""Pydantic models for the API surface — versioned shapes only."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    name: str
    byte_size: int
    created_at: str


class IngestResponse(BaseModel):
    document: DocumentOut
    chunks: int


class RetrievedChunkOut(BaseModel):
    chunk_id: int
    document_id: int
    ord: int
    text: str
    score: float


class MethodResultOut(BaseModel):
    method: str
    latency_ms: float
    build_ms: float
    index_size_bytes: int
    n_items: int
    chunks: list[RetrievedChunkOut]
    answer: str | None = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=50)
    methods: list[str] | None = None
    synthesize_answer: bool = True


class QueryResponse(BaseModel):
    question: str
    top_k: int
    results: list[MethodResultOut]


class EvalMethodMetrics(BaseModel):
    method: str
    recall_at_5: float
    recall_at_10: float
    mrr: float
    p50_latency_ms: float
    p95_latency_ms: float
    build_ms: float
    index_size_bytes: int


class EvalRunOut(BaseModel):
    id: int
    corpus_size: int
    created_at: str
    methods: list[EvalMethodMetrics]
