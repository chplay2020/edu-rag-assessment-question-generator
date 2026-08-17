"""Retrieval cho RAG.

`retrieve_context` là truy vấn đơn giản một lượt (giữ nguyên contract cũ).

`retrieve_diverse_context` là hàm pipeline nên dùng: nó chạy nhiều biến thể
truy vấn, gộp kết quả, ưu tiên chọn chunk thuộc các parent khác nhau và cắt
theo ngân sách ký tự. Ba việc này giải quyết đúng ba lỗi hay gặp khi sinh
nhiều câu hỏi từ một tài liệu:

1. Một truy vấn duy nhất chỉ chạm tới một góc của tài liệu -> câu hỏi bị lặp ý.
2. Top-k thuần similarity thường trả về các chunk chồng lấn nhau (do overlap
   khi chunking) -> context dư thừa mà vẫn nghèo thông tin.
3. Context quá dài làm tăng chi phí và khiến model bỏ qua phần giữa.

Ngoài ra, khi similarity không trả về gì (thường gặp lúc chạy embedding giả
hoặc Qdrant chưa index xong), hàm này rơi về việc quét thẳng chunk theo
material để pipeline vẫn có ngữ liệu thay vì fail.
"""

import logging
from dataclasses import dataclass
from collections.abc import Mapping, Sequence
from typing import Any, cast

from app.ai.embedding.embedder import embed_query
from app.ai.vector_store import get_vector_store
from app.core.config import settings


logger = logging.getLogger(__name__)

# Các "góc nhìn" thêm vào truy vấn gốc để phủ rộng tài liệu hơn.
QUERY_ASPECTS_VI = (
    "khái niệm và định nghĩa chính",
    "ví dụ và ứng dụng thực tế",
    "so sánh, phân loại và các bước thực hiện",
)
QUERY_ASPECTS_EN = (
    "key concepts and definitions",
    "examples and practical applications",
    "comparisons, classifications and procedures",
)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    material_id: int
    course_id: int
    content: str
    score: float
    payload: dict[str, Any]

    @property
    def parent_id(self) -> str:
        return str(self.payload.get("parent_id") or f"chunk-{self.chunk_id}")


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


# -- multi-query + diversity ---------------------------------------------


def expand_queries(query: str, *, language: str = "vi", limit: int = 3) -> list[str]:
    """Sinh thêm biến thể truy vấn quanh truy vấn gốc.

    Cố ý làm bằng luật thay vì gọi LLM: rẻ, xác định, không thêm điểm lỗi mạng
    vào đường đi chính, và đã đủ để phủ rộng một tài liệu học.
    """
    base = query.strip()
    if not base:
        return []

    aspects = QUERY_ASPECTS_VI if language.lower().startswith("vi") else QUERY_ASPECTS_EN
    queries = [base]
    for aspect in aspects[: max(limit - 1, 0)]:
        queries.append(f"{base} - {aspect}")
    return queries[:limit]


def _coerce_chunk(item: Any) -> RetrievedChunk | None:
    """Chuẩn hoá kết quả retrieval về RetrievedChunk.

    Chấp nhận cả RetrievedChunk, dict và object có thuộc tính tương ứng để
    hàm này dùng được với mọi cách mock retrieval trong test.
    """
    if isinstance(item, RetrievedChunk):
        return item

    chunk_id = _get_value(item, "chunk_id")
    if chunk_id is None:
        payload = _get_value(item, "payload", {}) or {}
        chunk_id = payload.get("chunk_id") if isinstance(payload, Mapping) else None
    if chunk_id is None:
        return None

    raw_payload = _get_value(item, "payload", {}) or {}
    payload = dict(raw_payload) if isinstance(raw_payload, Mapping) else {}

    return RetrievedChunk(
        chunk_id=int(chunk_id),
        material_id=int(_get_value(item, "material_id") or payload.get("material_id") or 0),
        course_id=int(_get_value(item, "course_id") or payload.get("course_id") or 0),
        content=str(_get_value(item, "content", "") or payload.get("content", "")),
        score=float(_get_value(item, "score", 0.0) or 0.0),
        payload=payload,
    )


def _fallback_material_chunks(
    *,
    material_id: int | None,
    course_id: int | None,
    limit: int,
) -> list[RetrievedChunk]:
    if material_id is None and course_id is None:
        return []
    try:
        payloads = get_vector_store().scroll_material_chunks(
            material_id=material_id,
            course_id=course_id,
            limit=limit,
        )
    except Exception as exc:
        # Fallback không được phép làm hỏng job: chỉ ghi log và trả rỗng.
        logger.warning("Fallback quét chunk theo material thất bại: %s", exc)
        return []

    chunks: list[RetrievedChunk] = []
    for payload in payloads:
        chunk = _coerce_chunk(payload)
        if chunk is not None and chunk.content.strip():
            chunks.append(chunk)
    return chunks


def _select_diverse(
    chunks: list[RetrievedChunk],
    *,
    top_k: int,
    max_context_chars: int,
) -> list[RetrievedChunk]:
    """Chọn chunk theo vòng tròn qua từng parent để tránh dồn vào một đoạn."""
    buckets: dict[str, list[RetrievedChunk]] = {}
    for chunk in sorted(chunks, key=lambda item: item.score, reverse=True):
        buckets.setdefault(chunk.parent_id, []).append(chunk)

    selected: list[RetrievedChunk] = []
    used_chars = 0
    while len(selected) < top_k:
        progressed = False
        for bucket in buckets.values():
            if not bucket or len(selected) >= top_k:
                continue
            chunk = bucket.pop(0)
            chunk_chars = len(chunk.content)
            if used_chars + chunk_chars > max_context_chars and selected:
                return selected
            selected.append(chunk)
            used_chars += chunk_chars
            progressed = True
        if not progressed:
            break

    return selected


def retrieve_diverse_context(
    query: str,
    *,
    material_id: int | None = None,
    course_id: int | None = None,
    top_k: int | None = None,
    language: str = "vi",
    max_context_chars: int | None = None,
    use_query_expansion: bool | None = None,
) -> list[RetrievedChunk]:
    top_k = top_k or settings.RAG_TOP_K
    max_context_chars = max_context_chars or settings.RAG_MAX_CONTEXT_CHARS
    if use_query_expansion is None:
        use_query_expansion = settings.RAG_QUERY_EXPANSION

    queries = (
        expand_queries(query, language=language)
        if use_query_expansion
        else [query.strip()]
    )
    queries = [item for item in queries if item]
    if not queries:
        raise ValueError("query must not be empty")

    merged: dict[int, RetrievedChunk] = {}
    for single_query in queries:
        try:
            # Gọi qua tên module-level để test có thể mock retrieve_context.
            results = retrieve_context(
                single_query,
                material_id=material_id,
                course_id=course_id,
                top_k=top_k,
            )
        except ValueError:
            raise
        except Exception as exc:
            logger.warning("Truy vấn retrieval '%s' thất bại: %s", single_query, exc)
            continue

        for item in results or []:
            chunk = _coerce_chunk(item)
            if chunk is None or not chunk.content.strip():
                continue
            if chunk.score < settings.RAG_MIN_SCORE:
                continue
            existing = merged.get(chunk.chunk_id)
            if existing is None or chunk.score > existing.score:
                merged[chunk.chunk_id] = chunk

    if not merged:
        logger.info(
            "Retrieval không trả về chunk nào cho material_id=%s, dùng fallback quét theo material.",
            material_id,
        )
        for chunk in _fallback_material_chunks(
            material_id=material_id,
            course_id=course_id,
            limit=top_k,
        ):
            merged.setdefault(chunk.chunk_id, chunk)

    return _select_diverse(
        list(merged.values()),
        top_k=top_k,
        max_context_chars=max_context_chars,
    )


def _chunk_header(chunk: Any) -> str:
    chunk_id = _get_value(chunk, "chunk_id", "unknown")
    material_id = _get_value(chunk, "material_id", "unknown")
    course_id = _get_value(chunk, "course_id", "unknown")
    try:
        score = float(_get_value(chunk, "score", 0.0) or 0.0)
    except (TypeError, ValueError):
        score = 0.0
    return (
        f"[chunk_id={chunk_id}; material_id={material_id}; "
        f"course_id={course_id}; score={score:.4f}]"
    )


def build_context_text(chunks: Sequence[Any]) -> str:
    """Ghép chunk thành context cho prompt.

    Nhận cả RetrievedChunk lẫn dict để phần generation không phải quan tâm
    retrieval trả về kiểu gì.
    """
    context_parts = []
    for chunk in chunks:
        content = _get_value(chunk, "content", "")
        context_parts.append(f"{_chunk_header(chunk)}\n{content}")
    return "\n\n".join(context_parts)


__all__ = [
    "RetrievedChunk",
    "build_context_text",
    "expand_queries",
    "retrieve_context",
    "retrieve_diverse_context",
]
