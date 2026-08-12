from dataclasses import dataclass, field
from typing import Any

from app.ai.embedding.embedder import embed_query
from app.ai.vector_store import get_vector_store


@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    matches: list[Any] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _score(match: Any) -> float:
    if isinstance(match, dict):
        return float(match.get("score", 0.0))
    return float(getattr(match, "score", 0.0))


def detect_duplicate_question(
    question_text: str,
    *,
    material_id: int | None = None,
    course_id: int | None = None,
    threshold: float = 0.92,
    top_k: int = 5,
) -> DuplicateCheckResult:
    text = question_text.strip()
    if not text:
        return DuplicateCheckResult(
            is_duplicate=False,
            warnings=["question_text is empty; duplicate check skipped"],
        )

    try:
        query_vector = embed_query(text)
        vector_store = get_vector_store()
        matches = vector_store.search_material_chunks(
            query_vector=query_vector,
            material_id=material_id,
            course_id=course_id,
            top_k=top_k,
        )
    except Exception as exc:
        return DuplicateCheckResult(
            is_duplicate=False,
            warnings=[f"duplicate check skipped: {exc}"],
        )

    matches_list = list(matches or [])
    is_duplicate = any(_score(match) >= threshold for match in matches_list)
    return DuplicateCheckResult(is_duplicate=is_duplicate, matches=matches_list)


__all__ = ["DuplicateCheckResult", "detect_duplicate_question"]
