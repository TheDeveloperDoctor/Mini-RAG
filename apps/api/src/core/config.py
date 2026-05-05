"""Centralised settings loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Runtime
    node_env: str = Field(default="development")
    log_level: str = Field(default="debug")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_cors_origins: str = Field(default="http://localhost:3000")

    # Storage
    sqlite_path: str = Field(default="./data/mini_rag.sqlite")
    faiss_index_dir: str = Field(default="./data/faiss")
    hf_home: str = Field(default="./.hf_cache")

    # Embeddings
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5")
    embedding_device: str = Field(default="cpu")

    # Chunking
    chunk_size: int = Field(default=500)
    chunk_overlap: int = Field(default=80)

    # LLM
    anthropic_api_key: str = Field(default="")
    answer_model: str = Field(default="claude-haiku-4-5-20251001")
    answer_max_tokens: int = Field(default=512)

    @property
    def is_production(self) -> bool:
        return self.node_env.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    def ensure_dirs(self) -> None:
        Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.faiss_index_dir).mkdir(parents=True, exist_ok=True)
        Path(self.hf_home).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
