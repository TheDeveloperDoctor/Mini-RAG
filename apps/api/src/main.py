"""FastAPI app factory — thin wiring only."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import documents as documents_router
from src.api import eval as eval_router
from src.api import query as query_router
from src.api.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from src.core.config import get_settings
from src.core.db import db_conn, init_db
from src.core.errors import register_error_handlers
from src.core.logger import Logger, get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    Logger.initialize()
    init_db()
    settings = get_settings()

    app = FastAPI(
        title="Mini RAG API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
    )

    # Order matters: outer middleware runs first on the request and last on
    # the response. RequestID has to be outermost so every other layer (and
    # error handlers) sees the request_id in logs.
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        capacity=settings.rate_limit_capacity,
        refill_per_sec=settings.rate_limit_refill_per_sec,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RequestIDMiddleware)

    register_error_handlers(app)

    app.include_router(documents_router.router)
    app.include_router(query_router.router)
    app.include_router(eval_router.router)

    @app.get("/healthz", tags=["health"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["health"])
    def readyz() -> JSONResponse:
        try:
            with db_conn() as conn:
                conn.execute("SELECT 1").fetchone()
        except Exception as exc:
            logger.exception("readiness_failed")
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "reason": str(exc)},
            )
        return JSONResponse(status_code=200, content={"status": "ready"})

    return app


app = create_app()
