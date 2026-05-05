"""FastAPI app factory — thin wiring only."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import documents as documents_router
from src.api import eval as eval_router
from src.api import query as query_router
from src.core.config import get_settings
from src.core.db import init_db
from src.core.errors import register_error_handlers
from src.core.logger import Logger


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(documents_router.router)
    app.include_router(query_router.router)
    app.include_router(eval_router.router)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
