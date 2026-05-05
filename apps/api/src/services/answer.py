"""Answer synthesis — Claude Haiku with retrieved chunks as context.

If ANTHROPIC_API_KEY is missing we degrade gracefully and return the top
retrieved chunk as the answer. Comparison lab still works without an LLM key.
"""
from __future__ import annotations

from src.core.config import get_settings
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

        try:
            import anthropic
        except ImportError:
            logger.warning("anthropic_sdk_missing")
            return self._fallback(chunks)

        context = "\n\n".join(
            f"[#{i + 1}] {c.text}" for i, c in enumerate(chunks)
        )
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        try:
            message = client.messages.create(
                model=settings.answer_model,
                max_tokens=settings.answer_max_tokens,
                system=_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}",
                    }
                ],
            )
        except Exception:
            logger.exception("anthropic_call_failed")
            return self._fallback(chunks)

        parts = [block.text for block in message.content if getattr(block, "type", None) == "text"]
        return "\n".join(parts).strip() or self._fallback(chunks)

    @staticmethod
    def _fallback(chunks: list[RetrievedChunk]) -> str:
        head = chunks[0].text.strip().replace("\n", " ")
        return f"(no LLM key set — top chunk) {head}"
