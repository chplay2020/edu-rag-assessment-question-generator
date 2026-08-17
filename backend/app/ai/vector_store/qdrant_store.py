"""Qdrant store cho hai collection:

- `material_chunks`: vector của các chunk học liệu, dùng cho retrieval.
- `question_vectors`: vector của các câu hỏi đã lưu, dùng cho duplicate
  detection trên toàn bộ ngân hàng câu hỏi.
"""

import logging
from dataclasses import dataclass
from typing import Any

from qdrant_client import models

from app.core.config import settings
from app.ai.vector_store.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)

# Các field được đánh index để filter theo material/course chạy nhanh trên tập lớn.
INDEXED_PAYLOAD_FIELDS = ("material_id", "course_id")


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


@dataclass(frozen=True)
class QuestionVector:
    question_id: int
    material_id: int
    course_id: int
    content: str
    difficulty: str | None = None
    bloom_level: str | None = None
    status: str | None = None


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


def build_question_payload(question: QuestionVector) -> dict[str, Any]:
    return {
        "question_id": question.question_id,
        "material_id": question.material_id,
        "course_id": question.course_id,
        "content": question.content,
        "difficulty": question.difficulty,
        "bloom_level": question.bloom_level,
        "status": question.status,
    }


def _build_filter(
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


def build_material_chunk_filter(
    *,
    material_id: int | None = None,
    course_id: int | None = None,
) -> models.Filter | None:
    return _build_filter(material_id=material_id, course_id=course_id)


def build_question_filter(
    *,
    material_id: int | None = None,
    course_id: int | None = None,
) -> models.Filter | None:
    return _build_filter(material_id=material_id, course_id=course_id)


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

    # -- schema ---------------------------------------------------------

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
            self._ensure_payload_indexes(collection_name)

    def _ensure_payload_indexes(self, collection_name: str) -> None:
        create_index = getattr(self.client, "create_payload_index", None)
        if create_index is None:
            return
        for field_name in INDEXED_PAYLOAD_FIELDS:
            try:
                create_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=models.PayloadSchemaType.INTEGER,
                )
            except Exception as exc:  # index đã tồn tại là trường hợp bình thường
                logger.debug(
                    "Bỏ qua tạo payload index %s.%s: %s",
                    collection_name,
                    field_name,
                    exc,
                )

    # -- material chunks ------------------------------------------------

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
        score_threshold: float | None = None,
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
            score_threshold=score_threshold,
        )
        return getattr(response, "points", response)

    def scroll_material_chunks(
        self,
        *,
        material_id: int | None = None,
        course_id: int | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Lấy chunk theo filter mà không cần vector.

        Dùng làm fallback khi retrieval theo similarity không trả về gì
        (ví dụ đang chạy embedding giả, hoặc câu truy vấn lệch chủ đề).
        """
        records, _next_offset = self.client.scroll(
            collection_name=self.material_collection,
            scroll_filter=_build_filter(material_id=material_id, course_id=course_id),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [dict(getattr(record, "payload", {}) or {}) for record in records]

    def get_material_chunks_by_ids(self, chunk_ids: list[int]) -> list[dict[str, Any]]:
        if not chunk_ids:
            return []

        response = self.client.retrieve(
            collection_name=self.material_collection,
            ids=chunk_ids,
            with_payload=True,
            with_vectors=False,
        )
        return [getattr(record, "payload", {}) for record in response]

    def delete_material_chunks(self, material_id: int) -> None:
        """Xoá vector cũ của material trước khi index lại, tránh chunk mồ côi."""
        self.client.delete(
            collection_name=self.material_collection,
            points_selector=models.FilterSelector(
                filter=_build_filter(material_id=material_id)
            ),
            wait=True,
        )

    # -- question bank --------------------------------------------------

    def upsert_question_vectors(
        self,
        questions: list[QuestionVector],
        vectors: list[list[float]],
    ) -> None:
        if len(questions) != len(vectors):
            raise ValueError("questions and vectors must have the same length")

        if not questions:
            return

        points = [
            models.PointStruct(
                id=question.question_id,
                vector=vectors[index],
                payload=build_question_payload(question),
            )
            for index, question in enumerate(questions)
        ]
        self.client.upsert(
            collection_name=self.question_collection,
            points=points,
            wait=True,
        )

    def search_questions(
        self,
        query_vector: list[float],
        *,
        material_id: int | None = None,
        course_id: int | None = None,
        top_k: int = 5,
        score_threshold: float | None = None,
    ) -> Any:
        response = self.client.query_points(
            collection_name=self.question_collection,
            query=query_vector,
            query_filter=build_question_filter(
                material_id=material_id,
                course_id=course_id,
            ),
            limit=top_k,
            with_payload=True,
            with_vectors=False,
            score_threshold=score_threshold,
        )
        return getattr(response, "points", response)


def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore()


__all__ = [
    "MaterialChunkVector",
    "QdrantVectorStore",
    "QuestionVector",
    "build_material_chunk_filter",
    "build_material_chunk_payload",
    "build_question_filter",
    "build_question_payload",
    "get_vector_store",
]
