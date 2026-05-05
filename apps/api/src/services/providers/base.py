"""Common provider contract.

Every provider takes a system prompt and a user prompt, returns a string.
Retry/timeout policy lives inside each provider so each can use the most
specific exception types from its own SDK.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.config import Settings


class ProviderError(Exception):
    """Permanent failure — caller should fall back, not retry."""


class AnswerProvider(ABC):
    name: str = "base"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """True when credentials/configuration are present."""

    @abstractmethod
    def synthesize(self, *, system: str, prompt: str) -> str:
        """Call the underlying LLM. Raise ProviderError on permanent failure."""
