"""Environment-aware structured logger.

Development -> debug+info+warn+error to console (and file if enabled).
Production  -> debug+info suppressed; warn+error always active. Silent failures
are not allowed — warn/error must reach the operator.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

from src.core.config import get_settings

_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord("", 0, "", 0, "", None, None).__dict__
            and k not in {"message", "asctime"}
        }
        if extras:
            payload["ctx"] = extras
        return json.dumps(payload, default=str)


class Logger:
    """Singleton logger keyed by name."""

    _initialised: bool = False
    _level: int = logging.DEBUG

    @classmethod
    def initialize(cls, file_path: str | None = None) -> None:
        if cls._initialised:
            return

        settings = get_settings()
        cls._level = cls._resolve_level(settings.log_level, settings.is_production)

        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(cls._level)

        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(_JsonFormatter())
        root.addHandler(stream)

        if file_path and not settings.is_production:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(_JsonFormatter())
            root.addHandler(file_handler)

        cls._initialised = True

    @classmethod
    def configure(cls, level: str) -> None:
        cls._level = cls._resolve_level(level, get_settings().is_production)
        logging.getLogger().setLevel(cls._level)

    @classmethod
    def get(cls, name: str) -> logging.Logger:
        if not cls._initialised:
            cls.initialize()
        return logging.getLogger(name)

    @classmethod
    def is_logging_enabled(cls, level: str) -> bool:
        target = _LEVEL_MAP.get(level.lower(), logging.INFO)
        return target >= cls._level

    @staticmethod
    def _resolve_level(configured: str, is_production: bool) -> int:
        if is_production:
            return logging.WARNING
        return _LEVEL_MAP.get(configured.lower(), logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    return Logger.get(name)
