from types import SimpleNamespace

import pytest

from app.ai.retrieval import retriever


def test_retrieve_context_embeds_query_and_searches_vector_store(monkeypatch):
    calls = {}

    class FakeVectorStore:
        def search_material_chunks(
            self,
            *,
            query_vector,
            material_id=None,
            course_id=None,
            top_k=5,
        ):
            calls["query_vector"] = query_vector
            calls["material_id"] = material_id
            calls["course_id"] = course_id
            calls["top_k"] = top_k
            return [
                SimpleNamespace(
                    id=99,
                    score=0.87,
                    payload={
                        "chunk_id": 10,
                        "material_id": 20,
                        "course_id": 30,
                        "content": "Retrieved context",
                    },
                )
            ]

    monkeypatch.setattr(retriever, "embed_query", lambda query: [0.1, 0.2, 0.3])
    monkeypatch.setattr(retriever, "get_vector_store", lambda: FakeVectorStore())

    chunks = retriever.retrieve_context(
        "operating system",
        material_id=20,
        course_id=30,
        top_k=3,
    )

    assert calls == {
        "query_vector": [0.1, 0.2, 0.3],
        "material_id": 20,
        "course_id": 30,
        "top_k": 3,
    }
    assert len(chunks) == 1
    assert chunks[0].chunk_id == 10
    assert chunks[0].material_id == 20
    assert chunks[0].course_id == 30
    assert chunks[0].content == "Retrieved context"
    assert chunks[0].score == 0.87


def test_retrieve_context_supports_dict_points(monkeypatch):
    class FakeVectorStore:
        def search_material_chunks(self, **kwargs):
            return [
                {
                    "id": 1,
                    "score": 0.5,
                    "payload": {
                        "chunk_id": 1,
                        "material_id": 2,
                        "course_id": 3,
                        "content": "Dict point content",
                    },
                }
            ]

    monkeypatch.setattr(retriever, "embed_query", lambda query: [0.1])
    monkeypatch.setattr(retriever, "get_vector_store", lambda: FakeVectorStore())

    chunks = retriever.retrieve_context("query")

    assert chunks[0].content == "Dict point content"
    assert chunks[0].score == 0.5


def test_build_context_text_includes_chunk_metadata():
    chunk = retriever.RetrievedChunk(
        chunk_id=1,
        material_id=2,
        course_id=3,
        content="Chunk content",
        score=0.91234,
        payload={},
    )

    context = retriever.build_context_text([chunk])

    assert "chunk_id=1" in context
    assert "material_id=2" in context
    assert "course_id=3" in context
    assert "score=0.9123" in context
    assert "Chunk content" in context


def test_retrieve_context_rejects_empty_query():
    with pytest.raises(ValueError, match="query must not be empty"):
        retriever.retrieve_context("   ")
