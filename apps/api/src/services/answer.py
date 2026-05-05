"""Answer synthesis — provider-agnostic with timeout + retry.

If the configured provider is missing a key (or the SDK fails to import) we
degrade gracefully and return the top retrieved chunk as the answer. The
comparison lab still works without an LLM key.
"""
from __future__ import annotations

from src.core.config import Settings, get_settings
from src.core.logger import get_logger
from src.services.retrieval import RetrievedChunk

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You answer questions strictly using the provided context chunks. "
    "Cite chunks as [#1], [#2] etc. matching their order. "
    "If the context does not contain the answer, say so plainly."
)


class AnswerService:
    def synthesize(self, *, question: str, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No context available."

        settings = get_settings()
        if not settings.anthropic_api_key:
            return self._fallback(chunks)

        context = "\n\n".join(f"[#{i + 1}] {c.text}" for i, c in enumerate(chunks))
        prompt = f"Context:\n{context}\n\nQuestion: {question}"

        try:
            return self._call_anthropic(prompt, settings)
        except _NonRetryable as exc:
            logger.warning("answer_provider_non_retryable", extra={"reason": str(exc)})
            return self._fallback(chunks)
        except Exception:
            logger.exception("answer_provider_failed")
            return self._fallback(chunks)

    @staticmethod
    def _fallback(chunks: list[RetrievedChunk]) -> str:
        head = chunks[0].text.strip().replace("\n", " ")
        return f"(no LLM available — top chunk) {head}"

    def _call_anthropic(self, prompt: str, settings: Settings) -> str:
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential_jitter,
        )

        try:
            import anthropic
        except ImportError as exc:
            raise _NonRetryable(f"anthropic_sdk_missing: {exc}") from exc

        # Don't retry hard client errors — they won't get better by retrying.
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
        def _do_call() -> str:
            client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key,
                timeout=settings.answer_timeout_sec,
            )
            try:
                message = client.messages.create(
                    model=settings.answer_model,
                    max_tokens=settings.answer_max_tokens,
                    system=_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )
            except non_retryable as exc:
                raise _NonRetryable(str(exc)) from exc

            parts = [
                block.text for block in message.content if getattr(block, "type", None) == "text"
            ]
            return "\n".join(parts).strip()

        result = _do_call()
        if not result:
            raise _NonRetryable("empty_response")
        return result


class _NonRetryable(Exception):
    """Raised for permanent failures we shouldn't retry (auth, bad req, etc)."""
