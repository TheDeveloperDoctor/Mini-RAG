"""Answer provider registry — pluggable LLM backends behind one interface.

Open/Closed: a new provider is one new file + one entry here. Routes and the
AnswerService are unaware of which provider answers a given request.
"""
from __future__ import annotations

from collections.abc import Callable

from src.core.config import Settings, get_settings
from src.core.logger import get_logger
from src.services.providers.anthropic import AnthropicProvider
from src.services.providers.base import AnswerProvider, ProviderError
from src.services.providers.openrouter import OpenRouterProvider

logger = get_logger(__name__)

_REGISTRY: dict[str, Callable[[Settings], AnswerProvider]] = {
    "anthropic": AnthropicProvider,
    "openrouter": OpenRouterProvider,
}

PROVIDER_NAMES: tuple[str, ...] = tuple(_REGISTRY.keys())


def make_provider(name: str, settings: Settings) -> AnswerProvider:
    factory = _REGISTRY.get(name.lower())
    if factory is None:
        raise KeyError(f"Unknown provider: {name}")
    return factory(settings)


def select_provider(settings: Settings | None = None) -> AnswerProvider | None:
    """Pick the configured provider; if unavailable, try the others.

    Returns None when no provider has credentials — caller falls back to the
    top retrieved chunk so the lab still works without an LLM key.
    """
    settings = settings or get_settings()
    preferred = settings.answer_provider.lower()
    order = [preferred] + [n for n in PROVIDER_NAMES if n != preferred]
    for name in order:
        try:
            provider = make_provider(name, settings)
        except KeyError:
            continue
        if provider.is_available:
            if name != preferred:
                logger.warning(
                    "answer_provider_fallback",
                    extra={"requested": preferred, "selected": name},
                )
            return provider
    return None


__all__ = [
    "AnswerProvider",
    "AnthropicProvider",
    "OpenRouterProvider",
    "ProviderError",
    "PROVIDER_NAMES",
    "make_provider",
    "select_provider",
]
