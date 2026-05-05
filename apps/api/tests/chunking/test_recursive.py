from __future__ import annotations

import pytest

from src.chunking.recursive import RecursiveChunker, chunk_text


class TestRecursiveChunker:
    def test_empty_text_returns_no_chunks(self) -> None:
        assert RecursiveChunker().split("") == []
        assert RecursiveChunker().split("   \n\n  ") == []

    def test_short_text_yields_single_chunk(self) -> None:
        result = RecursiveChunker(chunk_size=500).split("hello world")
        assert len(result) == 1
        assert result[0].text == "hello world"
        assert result[0].ord == 0

    def test_long_text_splits_into_multiple(self) -> None:
        text = "First paragraph.\n\n" + ("word " * 200) + "\n\nLast paragraph."
        chunks = RecursiveChunker(chunk_size=200, chunk_overlap=20).split(text)
        assert len(chunks) >= 2
        assert all(len(c.text) > 0 for c in chunks)
        assert [c.ord for c in chunks] == list(range(len(chunks)))

    def test_overlap_preserved(self) -> None:
        text = "A" * 50 + "\n\n" + "B" * 50 + "\n\n" + "C" * 50
        chunks = RecursiveChunker(chunk_size=60, chunk_overlap=10).split(text)
        assert len(chunks) >= 2

    def test_invalid_overlap_raises(self) -> None:
        with pytest.raises(ValueError):
            RecursiveChunker(chunk_size=100, chunk_overlap=200)

    def test_invalid_chunk_size_raises(self) -> None:
        with pytest.raises(ValueError):
            RecursiveChunker(chunk_size=0)

    def test_helper_function_works(self) -> None:
        chunks = chunk_text("hello world", chunk_size=100, chunk_overlap=10)
        assert chunks[0].text == "hello world"
