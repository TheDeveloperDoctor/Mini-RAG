from __future__ import annotations

import numpy as np

from src.repositories.chunk import ChunkRepository
from src.repositories.document import DocumentRepository
from src.repositories.eval_run import EvalRunRepository


class TestDocumentRepository:
    def test_create_and_fetch(self) -> None:
        repo = DocumentRepository()
        doc = repo.create(name="alpha.txt", byte_size=42)
        assert doc.id > 0
        assert doc.name == "alpha.txt"
        again = repo.get(doc.id)
        assert again is not None
        assert again.id == doc.id

    def test_list_orders_newest_first(self) -> None:
        repo = DocumentRepository()
        a = repo.create(name="a", byte_size=1)
        b = repo.create(name="b", byte_size=2)
        ids = [d.id for d in repo.list_all()]
        assert ids[0] == b.id
        assert ids[-1] == a.id

    def test_get_missing_returns_none(self) -> None:
        assert DocumentRepository().get(99999) is None


class TestChunkRepository:
    def test_bulk_insert_then_read_back(self) -> None:
        docs = DocumentRepository()
        chunks = ChunkRepository()
        doc = docs.create(name="x.txt", byte_size=10)

        vecs = [np.ones(8, dtype=np.float32) * (i + 1) for i in range(3)]
        items = [(i, f"text-{i}", vecs[i]) for i in range(3)]
        n = chunks.bulk_insert(document_id=doc.id, items=items)
        assert n == 3
        assert chunks.count() == 3

        all_chunks = chunks.all_chunks()
        assert len(all_chunks) == 3
        assert all_chunks[0].text == "text-0"
        np.testing.assert_array_equal(all_chunks[0].embedding, vecs[0])

    def test_bulk_insert_empty_no_op(self) -> None:
        n = ChunkRepository().bulk_insert(document_id=1, items=[])
        assert n == 0


class TestEvalRunRepository:
    def test_create_and_latest(self) -> None:
        repo = EvalRunRepository()
        record = repo.create(corpus_size=10, results={"methods": [{"method": "naive"}]})
        latest = repo.latest()
        assert latest is not None
        assert latest.id == record.id
        assert latest.results["methods"][0]["method"] == "naive"

    def test_latest_when_empty(self) -> None:
        assert EvalRunRepository().latest() is None
