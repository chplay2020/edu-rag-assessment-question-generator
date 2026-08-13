from typing import Literal, TypeAlias


BloomLevel: TypeAlias = Literal[
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]

BLOOM_LEVELS: set[str] = {
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
}

DIFFICULTY_LEVELS: set[str] = {"easy", "medium", "hard"}

_BLOOM_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("create", ("thiết kế", "tạo", "xây dựng", "đề xuất", "sáng tạo", "design", "create", "construct")),
    ("evaluate", ("đánh giá", "phê bình", "so sánh ưu nhược", "evaluate", "justify", "critique")),
    ("analyze", ("phân tích", "phân biệt", "nguyên nhân", "quan hệ", "analyze", "differentiate")),
    ("apply", ("áp dụng", "tính", "sử dụng", "vận dụng", "apply", "use", "calculate")),
    ("understand", ("giải thích", "mô tả", "tóm tắt", "hiểu", "explain", "describe", "summarize")),
    ("remember", ("là gì", "nêu", "liệt kê", "định nghĩa", "what is", "define", "list")),
]


def normalize_bloom_level(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized if normalized in BLOOM_LEVELS else None


def classify_bloom_level(question_text: str) -> str:
    text = question_text.lower()
    for level, keywords in _BLOOM_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return level
    return "understand"


def normalize_difficulty(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized if normalized in DIFFICULTY_LEVELS else None


def classify_difficulty(question_text: str, bloom_level: str | None = None) -> str:
    text = question_text.lower()
    bloom = normalize_bloom_level(bloom_level)

    if bloom in {"evaluate", "create"}:
        return "hard"
    if bloom in {"apply", "analyze"}:
        return "medium"
    if any(keyword in text for keyword in ("phân tích", "đánh giá", "so sánh", "analyze", "evaluate")):
        return "hard"
    if any(keyword in text for keyword in ("áp dụng", "giải thích", "apply", "explain")):
        return "medium"
    return "easy"


__all__ = [
    "BLOOM_LEVELS",
    "DIFFICULTY_LEVELS",
    "classify_bloom_level",
    "classify_difficulty",
    "normalize_bloom_level",
    "normalize_difficulty",
]
