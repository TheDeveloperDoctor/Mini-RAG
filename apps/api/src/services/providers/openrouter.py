"""OpenRouter provider — OpenAI-compatible chat completions over httpx.

OpenRouter's API mirrors OpenAI's `/v1/chat/completions`, so we hit it
directly with httpx instead of pulling in a second SDK. The HTTP-Referer
and X-Title headers are recommended by OpenRouter for rate-limit attribution
and analytics.
"""
from __future__ import annotations

import httpx

from src.core.logger import get_logger
from src.services.providers.base import AnswerProvider, ProviderError

logger = get_logger(__name__)

_RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504}


class OpenRouterProvider(AnswerProvider):
    name = "openrouter"

    @property
    def is_available(self) -> bool:
        return bool(self._settings.openrouter_api_key)

    def synthesize(self, *, system: str, prompt: str) -> str:
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential_jitter,
        )

        url = self._settings.openrouter_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._settings.openrouter_referer,
            "X-Title": self._settings.openrouter_app_title,
        }
        payload = {
            "model": self._settings.openrouter_model,
            "max_tokens": self._settings.answer_max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential_jitter(initial=0.5, max=4.0),
            retry=retry_if_exception_type((httpx.TransportError, _Retryable)),
            reraise=True,
        )
        def _call() -> str:
            try:
                response = httpx.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self._settings.answer_timeout_sec,
                )
            except httpx.TimeoutException as exc:
                raise _Retryable(f"timeout: {exc}") from exc

            if response.status_code in _RETRY_STATUS:
                raise _Retryable(f"openrouter {response.status_code}: {response.text[:200]}")
            if response.status_code >= 400:
                raise ProviderError(
                    f"openrouter {response.status_code}: {response.text[:200]}"
                )

            try:
                body = response.json()
            except ValueError as exc:
                raise ProviderError(f"openrouter non-json response: {exc}") from exc

            text = _extract_content(body)
            if not text:
                raise ProviderError("openrouter returned empty content")
            return text

        try:
            return _call()
        except _Retryable as exc:
            raise ProviderError(f"openrouter retries exhausted: {exc}") from exc


class _Retryable(Exception):
    """Wraps transient OpenRouter failures so tenacity retries them."""


def _extract_content(body: dict[str, object]) -> str:
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    # Some models return content as a list of parts {"type":"text","text":"..."}
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text = part.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()
    return ""
