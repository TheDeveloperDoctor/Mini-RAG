"""Anthropic provider — Claude Messages API with retry + timeout."""
from __future__ import annotations

from src.core.logger import get_logger
from src.services.providers.base import AnswerProvider, ProviderError

logger = get_logger(__name__)


class AnthropicProvider(AnswerProvider):
    name = "anthropic"

    @property
    def is_available(self) -> bool:
        return bool(self._settings.anthropic_api_key)

    def synthesize(self, *, system: str, prompt: str) -> str:
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential_jitter,
        )

        try:
            import anthropic
        except ImportError as exc:
            raise ProviderError(f"anthropic_sdk_missing: {exc}") from exc

        non_retryable = (
            anthropic.AuthenticationError,
            anthropic.BadRequestError,
            anthropic.PermissionDeniedError,
            anthropic.NotFoundError,
        )

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential_jitter(initial=0.5, max=4.0),
            retry=retry_if_exception_type(
                (
                    anthropic.APIConnectionError,
                    anthropic.APITimeoutError,
                    anthropic.RateLimitError,
                    anthropic.InternalServerError,
                )
            ),
            reraise=True,
        )
        def _call() -> str:
            client = anthropic.Anthropic(
                api_key=self._settings.anthropic_api_key,
                timeout=self._settings.answer_timeout_sec,
            )
            try:
                message = client.messages.create(
                    model=self._settings.answer_model,
                    max_tokens=self._settings.answer_max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
            except non_retryable as exc:
                raise ProviderError(str(exc)) from exc

            parts = [
                block.text for block in message.content if getattr(block, "type", None) == "text"
            ]
            text = "\n".join(parts).strip()
            if not text:
                raise ProviderError("anthropic returned empty response")
            return text

        return _call()
