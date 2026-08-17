"""Phân loại/chuẩn hoá Bloom level và độ khó (T043, T044).

Dùng luật từ khoá thay vì gọi LLM: chạy tức thì, không tốn quota, và trong
pipeline nó chỉ đóng vai trò "lưới an toàn" - chỉnh lại nhãn khi LLM trả về
giá trị ngoài danh mục, chứ không ghi đè nhãn hợp lệ do LLM đưa ra.
"""

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

# Ánh xạ các biến thể mà LLM hay trả về sai chính tả/khác ngôn ngữ.
_BLOOM_ALIASES: dict[str, str] = {
    "recall": "remember",
    "knowledge": "remember",
    "memorize": "remember",
    "nhớ": "remember",
    "comprehend": "understand",
    "comprehension": "understand",
    "hiểu": "understand",
    "application": "apply",
    "vận dụng": "apply",
    "analysis": "analyze",
    "analyse": "analyze",
    "phân tích": "analyze",
    "evaluation": "evaluate",
    "đánh giá": "evaluate",
    "synthesis": "create",
    "creating": "create",
    "sáng tạo": "create",
}

_DIFFICULTY_ALIASES: dict[str, str] = {
    "dễ": "easy",
    "de": "easy",
    "low": "easy",
    "beginner": "easy",
    "trung bình": "medium",
    "normal": "medium",
    "moderate": "medium",
    "intermediate": "medium",
    "khó": "hard",
    "kho": "hard",
    "high": "hard",
    "difficult": "hard",
    "advanced": "hard",
}


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


def coerce_bloom_level(value: str | None, question_text: str = "") -> str:
    """Đưa mọi giá trị về đúng danh mục Bloom, suy luận nếu cần."""
    normalized = normalize_bloom_level(value)
    if normalized:
        return normalized
    if value:
        alias = _BLOOM_ALIASES.get(value.strip().lower())
        if alias:
            return alias
    return classify_bloom_level(question_text)


def coerce_difficulty(
    value: str | None,
    question_text: str = "",
    bloom_level: str | None = None,
) -> str:
    normalized = normalize_difficulty(value)
    if normalized:
        return normalized
    if value:
        alias = _DIFFICULTY_ALIASES.get(value.strip().lower())
        if alias:
            return alias
    return classify_difficulty(question_text, bloom_level)


def refine_labels(
    question_text: str,
    *,
    difficulty: str | None,
    bloom_level: str | None,
) -> tuple[str, str]:
    """Trả về `(difficulty, bloom_level)` luôn nằm trong danh mục hợp lệ."""
    bloom = coerce_bloom_level(bloom_level, question_text)
    return coerce_difficulty(difficulty, question_text, bloom), bloom


__all__ = [
    "BLOOM_LEVELS",
    "DIFFICULTY_LEVELS",
    "classify_bloom_level",
    "classify_difficulty",
    "coerce_bloom_level",
    "coerce_difficulty",
    "normalize_bloom_level",
    "normalize_difficulty",
    "refine_labels",
]
