from dataclasses import dataclass
from collections.abc import Mapping, Sequence
from typing import Any, cast

from app.ai.embedding.embedder import embed_query
from app.ai.vector_store import get_vector_store


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    material_id: int
    course_id: int
    content: str
    score: float
    payload: dict[str, Any]


def _get_value(source: Any, key: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def _point_to_retrieved_chunk(point: Any) -> RetrievedChunk:
    raw_payload = _get_value(point, "payload", {}) or {}
    if isinstance(raw_payload, Mapping):
        payload: dict[str, Any] = dict(raw_payload)
    else:
        raise ValueError("retrieved point payload must be a mapping")

    chunk_id = payload.get("chunk_id", _get_value(point, "id"))
    material_id = payload.get("material_id")
    course_id = payload.get("course_id")
    content = payload.get("content", "")
    score = _get_value(point, "score", 0.0)
    if chunk_id is None or material_id is None or course_id is None:
        raise ValueError("retrieved point payload is missing required IDs")

    return RetrievedChunk(
        chunk_id=int(chunk_id),
        material_id=int(material_id),
        course_id=int(course_id),
        content=str(content),
        score=float(score),
        payload=payload,
    )


def retrieve_context(
    query: str,
    *,
    material_id: int | None = None,
    course_id: int | None = None,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    query_text = query.strip()
    if not query_text:
        raise ValueError("query must not be empty")
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    query_vector = embed_query(query_text)
    vector_store = get_vector_store()
    results = cast(
        Sequence[Any],
        vector_store.search_material_chunks(
            query_vector=query_vector,
            material_id=material_id,
            course_id=course_id,
            top_k=top_k,
        ),
    )

    return [_point_to_retrieved_chunk(point) for point in results]


def build_context_text(chunks: list[RetrievedChunk]) -> str:
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[chunk_id={chunk.chunk_id}; material_id={chunk.material_id}; "
            f"course_id={chunk.course_id}; score={chunk.score:.4f}]\n{chunk.content}"
        )
    return "\n\n".join(context_parts)


__all__ = ["RetrievedChunk", "build_context_text", "retrieve_context"]
