"""Phát hiện câu hỏi trùng lặp (T045, T069).

Hai lớp bảo vệ:

1. `find_near_duplicates_in_batch`: so khớp text đã chuẩn hoá ngay trong lô
   vừa sinh. Không cần embedding nên vẫn hoạt động khi đang chạy provider
   embedding giả - đây là lỗi trùng hay gặp nhất khi sinh nhiều câu một lượt.
2. `detect_duplicate_question`: so với ngân hàng câu hỏi đã lưu trong Qdrant
   (collection `question_vectors`). Chỉ đáng tin khi dùng embedding thật.

Cả hai đều "fail-open": Qdrant lỗi thì cảnh báo chứ không làm hỏng job sinh
câu hỏi.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any, Sequence

from app.ai.embedding.embedder import embed_query
from app.ai.vector_store import get_vector_store
from app.core.config import settings


@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    matches: list[Any] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _token_overlap(first: str, second: str) -> float:
    first_tokens = set(first.split())
    second_tokens = set(second.split())
    if not first_tokens or not second_tokens:
        return 0.0
    return len(first_tokens & second_tokens) / len(first_tokens | second_tokens)


def text_similarity(first: str, second: str) -> float:
    """Độ giống của hai câu hỏi, trong khoảng 0.0-1.0.

    Lấy giá trị nhỏ hơn giữa tỉ lệ khớp ký tự và tỉ lệ trùng từ. Chỉ dùng khớp
    ký tự sẽ báo trùng nhầm cho hai câu ngắn khác nhau đúng một từ khoá
    ("bộ nhớ ảo là gì" và "bộ nhớ đệm là gì" giống nhau tới 88% ký tự), trong
    khi tỉ lệ trùng từ nhìn ra ngay chúng hỏi về hai khái niệm khác nhau.
    """
    first_normalized = normalize_text(first)
    second_normalized = normalize_text(second)
    return min(
        SequenceMatcher(None, first_normalized, second_normalized).ratio(),
        _token_overlap(first_normalized, second_normalized),
    )


def _score(match: Any) -> float:
    if isinstance(match, dict):
        return float(match.get("score", 0.0))
    return float(getattr(match, "score", 0.0))


def _match_id(match: Any) -> Any:
    if isinstance(match, dict):
        return match.get("id")
    return getattr(match, "id", None)


def find_near_duplicates_in_batch(
    question_texts: Sequence[str],
    *,
    threshold: float | None = None,
) -> set[int]:
    """Trả về index của các câu trùng với một câu đứng trước trong lô."""
    limit = threshold if threshold is not None else settings.NEAR_DUPLICATE_TEXT_RATIO
    duplicates: set[int] = set()
    kept: list[str] = []

    for index, text in enumerate(question_texts):
        normalized = normalize_text(text)
        if not normalized:
            continue
        if any(
            min(
                SequenceMatcher(None, normalized, other).ratio(),
                _token_overlap(normalized, other),
            )
            >= limit
            for other in kept
        ):
            duplicates.add(index)
            continue
        kept.append(normalized)

    return duplicates


def detect_duplicate_question(
    question_text: str,
    *,
    material_id: int | None = None,
    course_id: int | None = None,
    exclude_question_id: int | None = None,
    threshold: float | None = None,
    top_k: int = 5,
) -> DuplicateCheckResult:
    text = question_text.strip()
    if not text:
        return DuplicateCheckResult(
            is_duplicate=False,
            warnings=["question_text is empty; duplicate check skipped"],
        )

    limit = threshold if threshold is not None else settings.DUPLICATE_THRESHOLD

    try:
        query_vector = embed_query(text)
        vector_store = get_vector_store()
        # So với ngân hàng câu hỏi khi store hỗ trợ; nếu không thì rơi về
        # collection chunk để giữ tương thích ngược.
        search_questions = getattr(vector_store, "search_questions", None)
        if callable(search_questions):
            matches = search_questions(
                query_vector=query_vector,
                course_id=course_id,
                status="approved",
                top_k=top_k,
            )
        else:
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
    if exclude_question_id is not None:
        matches_list = [m for m in matches_list if _match_id(m) != exclude_question_id]
        
    is_duplicate = any(_score(match) >= limit for match in matches_list)
    return DuplicateCheckResult(is_duplicate=is_duplicate, matches=matches_list)


__all__ = [
    "DuplicateCheckResult",
    "detect_duplicate_question",
    "find_near_duplicates_in_batch",
    "normalize_text",
    "text_similarity",
]
