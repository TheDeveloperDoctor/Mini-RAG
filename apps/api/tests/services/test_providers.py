"""Tests for the provider strategy: selection logic, OpenRouter HTTP shape,
and AnswerService fallback behaviour."""
from __future__ import annotations

from typing import Any

import httpx
import pytest

from src.core.config import get_settings
from src.services.answer import AnswerService
from src.services.providers import (
    PROVIDER_NAMES,
    AnthropicProvider,
    OpenRouterProvider,
    make_provider,
    select_provider,
)
from src.services.providers.base import ProviderError
from src.services.providers.openrouter import _extract_content
from src.services.retrieval import RetrievedChunk


def _chunk(text: str = "Photosynthesis is the process") -> RetrievedChunk:
    return RetrievedChunk(chunk_id=1, document_id=1, ord=0, text=text, score=0.9)


class TestProviderRegistry:
    def test_registry_lists_both_providers(self) -> None:
        assert set(PROVIDER_NAMES) == {"anthropic", "openrouter"}

    def test_make_unknown_raises(self) -> None:
        with pytest.raises(KeyError):
            make_provider("does-not-exist", get_settings())


class TestProviderSelection:
    def test_no_keys_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("OPENROUTER_API_KEY", "")
        get_settings.cache_clear()
        assert select_provider() is None

    def test_prefers_configured_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANSWER_PROVIDER", "openrouter")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        get_settings.cache_clear()
        provider = select_provider()
        assert isinstance(provider, OpenRouterProvider)

    def test_falls_back_when_preferred_missing_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANSWER_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        get_settings.cache_clear()
        provider = select_provider()
        assert isinstance(provider, OpenRouterProvider)

    def test_anthropic_picked_when_both_keys_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANSWER_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "ant-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
        get_settings.cache_clear()
        provider = select_provider()
        assert isinstance(provider, AnthropicProvider)


class TestOpenRouterCall:
    def test_synthesize_uses_correct_url_headers_and_payload(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-test-key")
        monkeypatch.setenv("OPENROUTER_MODEL", "vendor/model-x")
        monkeypatch.setenv("OPENROUTER_BASE_URL", "https://router.test/v1")
        monkeypatch.setenv("OPENROUTER_REFERER", "https://example.com")
        get_settings.cache_clear()

        captured: dict[str, Any] = {}

        def fake_post(url: str, **kwargs: Any) -> httpx.Response:
            captured["url"] = url
            captured["headers"] = kwargs.get("headers")
            captured["json"] = kwargs.get("json")
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "hello world"}}]},
            )

        monkeypatch.setattr(httpx, "post", fake_post)

        provider = OpenRouterProvider(get_settings())
        result = provider.synthesize(system="sys", prompt="hi")

        assert result == "hello world"
        assert captured["url"] == "https://router.test/v1/chat/completions"
        assert captured["headers"]["Authorization"] == "Bearer or-test-key"
        assert captured["headers"]["HTTP-Referer"] == "https://example.com"
        assert captured["json"]["model"] == "vendor/model-x"
        assert captured["json"]["messages"][0] == {"role": "system", "content": "sys"}
        assert captured["json"]["messages"][1] == {"role": "user", "content": "hi"}

    def test_4xx_raises_provider_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-test")
        get_settings.cache_clear()

        def fake_post(*_: Any, **__: Any) -> httpx.Response:
            return httpx.Response(401, text="unauthorised")

        monkeypatch.setattr(httpx, "post", fake_post)

        provider = OpenRouterProvider(get_settings())
        with pytest.raises(ProviderError):
            provider.synthesize(system="s", prompt="p")

    def test_extracts_list_content_format(self) -> None:
        body = {
            "choices": [
                {"message": {"content": [{"type": "text", "text": "part one"}]}}
            ]
        }
        assert _extract_content(body) == "part one"


class TestAnswerServiceFallback:
    def test_no_provider_returns_top_chunk_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("OPENROUTER_API_KEY", "")
        get_settings.cache_clear()

        result = AnswerService().synthesize(question="q?", chunks=[_chunk()])
        assert "top chunk" in result.lower()

    def test_provider_error_falls_back(self) -> None:
        class BoomProvider:
            name = "boom"

            @property
            def is_available(self) -> bool:
                return True

            def synthesize(self, *, system: str, prompt: str) -> str:
                raise ProviderError("network down")

        result = AnswerService(provider=BoomProvider()).synthesize(  # type: ignore[arg-type]
            question="q?", chunks=[_chunk()]
        )
        assert "top chunk" in result.lower()

    def test_provider_success_returned_verbatim(self) -> None:
        class OkProvider:
            name = "ok"

            @property
            def is_available(self) -> bool:
                return True

            def synthesize(self, *, system: str, prompt: str) -> str:
                return "synthesised answer"

        result = AnswerService(provider=OkProvider()).synthesize(  # type: ignore[arg-type]
            question="q?", chunks=[_chunk()]
        )
        assert result == "synthesised answer"
