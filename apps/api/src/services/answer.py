"""Answer synthesis — provider-agnostic with graceful fallback.

The provider is picked by `select_provider()` based on `ANSWER_PROVIDER` and
which API keys are present. With zero providers configured we degrade to
returning the top retrieved chunk so the comparison lab still works offline.
"""
from __future__ import annotations

from src.core.logger import get_logger
from src.services.providers import AnswerProvider, ProviderError, select_provider
from src.services.retrieval import RetrievedChunk

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You answer questions strictly using the provided context chunks. "
    "Cite chunks as [#1], [#2] etc. matching their order. "
    "If the context does not contain the answer, say so plainly."
)


class AnswerService:
    def __init__(self, provider: AnswerProvider | None = None) -> None:
        self._provider_override = provider

    def synthesize(self, *, question: str, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No context available."

        provider = self._provider_override or select_provider()
        if provider is None:
            return self._fallback(chunks)

        context = "\n\n".join(f"[#{i + 1}] {c.text}" for i, c in enumerate(chunks))
        prompt = f"Context:\n{context}\n\nQuestion: {question}"

        try:
            answer = provider.synthesize(system=_SYSTEM_PROMPT, prompt=prompt)
        except ProviderError as exc:
            logger.warning(
                "answer_provider_error",
                extra={"provider": provider.name, "reason": str(exc)},
            )
            return self._fallback(chunks)
        except Exception:
            logger.exception("answer_provider_unexpected", extra={"provider": provider.name})
            return self._fallback(chunks)

        return answer

    @staticmethod
    def _fallback(chunks: list[RetrievedChunk]) -> str:
        head = chunks[0].text.strip().replace("\n", " ")
        return f"(no LLM available — top chunk) {head}"
