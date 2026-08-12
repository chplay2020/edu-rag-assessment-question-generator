from dataclasses import dataclass
from typing import Any

from qdrant_client import models

from app.core.config import settings
from app.ai.vector_store.qdrant_client import get_qdrant_client


@dataclass(frozen=True)
class MaterialChunkVector:
    chunk_id: int
    material_id: int
    course_id: int
    chunk_index: int
    content: str
    parent_id: str | None = None
    child_index: int | None = None
    chunk_type: str = "child"


def build_material_chunk_payload(chunk: MaterialChunkVector) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "parent_id": chunk.parent_id,
        "material_id": chunk.material_id,
        "course_id": chunk.course_id,
        "chunk_index": chunk.chunk_index,
        "child_index": chunk.child_index,
        "chunk_type": chunk.chunk_type,
        "content": chunk.content,
    }


def build_material_chunk_filter(
    *,
    material_id: int | None = None,
    course_id: int | None = None,
) -> models.Filter | None:
    conditions: list[models.FieldCondition] = []
    if material_id is not None:
        conditions.append(
            models.FieldCondition(
                key="material_id",
                match=models.MatchValue(value=material_id),
            )
        )
    if course_id is not None:
        conditions.append(
            models.FieldCondition(
                key="course_id",
                match=models.MatchValue(value=course_id),
            )
        )

    if not conditions:
        return None
    return models.Filter(must=conditions)


class QdrantVectorStore:
    def __init__(
        self,
        *,
        client: Any | None = None,
        material_collection: str | None = None,
        question_collection: str | None = None,
        vector_size: int | None = None,
    ) -> None:
        self.client = client or get_qdrant_client()
        self.material_collection = (
            material_collection or settings.QDRANT_MATERIAL_COLLECTION
        )
        self.question_collection = (
            question_collection or settings.QDRANT_QUESTION_COLLECTION
        )
        self.vector_size = vector_size or settings.EMBEDDING_DIMENSION

    def ensure_collections(self) -> None:
        vector_config = models.VectorParams(
            size=self.vector_size,
            distance=models.Distance.COSINE,
        )
        for collection_name in [
            self.material_collection,
            self.question_collection,
        ]:
            if not self.client.collection_exists(collection_name=collection_name):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=vector_config,
                )

    def upsert_material_chunks(
        self,
        chunks: list[MaterialChunkVector],
        vectors: list[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")

        if not chunks:
            return

        points = [
            models.PointStruct(
                id=chunk.chunk_id,
                vector=vectors[index],
                payload=build_material_chunk_payload(chunk),
            )
            for index, chunk in enumerate(chunks)
        ]
        self.client.upsert(
            collection_name=self.material_collection,
            points=points,
            wait=True,
        )

    def search_material_chunks(
        self,
        query_vector: list[float],
        *,
        material_id: int | None = None,
        course_id: int | None = None,
        top_k: int = 5,
    ) -> Any:
        query_filter = build_material_chunk_filter(
            material_id=material_id,
            course_id=course_id,
        )
        response = self.client.query_points(
            collection_name=self.material_collection,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        return getattr(response, "points", response)


def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore()


__all__ = [
    "MaterialChunkVector",
    "QdrantVectorStore",
    "build_material_chunk_filter",
    "build_material_chunk_payload",
    "get_vector_store",
]
