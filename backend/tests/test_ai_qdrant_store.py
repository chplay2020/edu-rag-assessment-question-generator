from types import SimpleNamespace

from app.ai.vector_store.qdrant_store import (
    MaterialChunkVector,
    QdrantVectorStore,
    build_material_chunk_filter,
    build_material_chunk_payload,
)


def test_build_qdrant_material_chunk_payload():
    chunk = MaterialChunkVector(
        chunk_id=1,
        parent_id="parent-0",
        material_id=2,
        course_id=3,
        chunk_index=4,
        child_index=5,
        chunk_type="child",
        content="Chunk content",
    )

    payload = build_material_chunk_payload(chunk)

    assert payload == {
        "chunk_id": 1,
        "parent_id": "parent-0",
        "material_id": 2,
        "course_id": 3,
        "chunk_index": 4,
        "child_index": 5,
        "chunk_type": "child",
        "content": "Chunk content",
    }


def test_qdrant_filter_material_id_and_course_id():
    query_filter = build_material_chunk_filter(material_id=10, course_id=20)

    assert query_filter is not None
    conditions = query_filter.must or []
    assert len(conditions) == 2
    assert conditions[0].key == "material_id"
    assert conditions[0].match.value == 10
    assert conditions[1].key == "course_id"
    assert conditions[1].match.value == 20


def test_search_material_chunks_passes_qdrant_filter():
    class FakeClient:
        def __init__(self):
            self.query_kwargs = None

        def query_points(self, **kwargs):
            self.query_kwargs = kwargs
            return SimpleNamespace(points=["result"])

    client = FakeClient()
    store = QdrantVectorStore(
        client=client,
        material_collection="material_chunks",
        vector_size=3,
    )

    results = store.search_material_chunks(
        [0.1, 0.2, 0.3],
        material_id=1,
        course_id=2,
        top_k=7,
    )

    assert results == ["result"]
    assert client.query_kwargs["collection_name"] == "material_chunks"
    assert client.query_kwargs["limit"] == 7
    conditions = client.query_kwargs["query_filter"].must
    assert [condition.key for condition in conditions] == ["material_id", "course_id"]


def test_upsert_material_chunks_builds_points():
    class FakeClient:
        def __init__(self):
            self.upsert_kwargs = None

        def upsert(self, **kwargs):
            self.upsert_kwargs = kwargs

    client = FakeClient()
    store = QdrantVectorStore(
        client=client,
        material_collection="material_chunks",
        vector_size=3,
    )
    chunk = MaterialChunkVector(
        chunk_id=9,
        material_id=1,
        course_id=2,
        chunk_index=0,
        content="Chunk",
    )

    store.upsert_material_chunks([chunk], [[0.1, 0.2, 0.3]])

    point = client.upsert_kwargs["points"][0]
    assert client.upsert_kwargs["collection_name"] == "material_chunks"
    assert point.id == 9
    assert point.vector == [0.1, 0.2, 0.3]
    assert point.payload["chunk_id"] == 9
