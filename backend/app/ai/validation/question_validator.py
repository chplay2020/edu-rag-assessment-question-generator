"""Kiểm tra câu hỏi bằng luật (T041).

Hai mức độ:

- `errors`: câu hỏi sai hợp đồng MCQ -> pipeline loại bỏ câu đó.
- `warnings`: câu hỏi dùng được nhưng chất lượng đáng ngờ -> lưu ở trạng thái
  `review_required` để giảng viên xem lại.

Nhóm luật chất lượng ở đây bắt đúng những lỗi mà LLM hay mắc khi sinh MCQ:
đáp án đúng dài hơn hẳn các phương án nhiễu (học sinh đoán được mà không cần
học), phương án trùng nhau, "tất cả các đáp án trên", và câu hỏi tham chiếu
ngược vào tài liệu nên không đứng độc lập được.
"""

from dataclasses import dataclass, field
from typing import Any, Iterable

from app.ai.generation.output_parser import GeneratedQuestionBatch
from app.ai.validation.bloom_classifier import BLOOM_LEVELS, DIFFICULTY_LEVELS


MIN_QUESTION_TEXT_LENGTH = 10
MIN_EXPLANATION_LENGTH = 15
# Đáp án đúng dài hơn phương án nhiễu dài nhất quá tỉ lệ này -> lộ đáp án.
MAX_CORRECT_LENGTH_RATIO = 2.5

BANNED_OPTION_PHRASES = (
    "tất cả các đáp án trên",
    "tất cả các phương án trên",
    "không đáp án nào",
    "không có đáp án nào",
    "all of the above",
    "none of the above",
    "both a and b",
)
SELF_REFERENCE_PHRASES = (
    "theo đoạn văn",
    "theo đoạn trích",
    "trong ngữ cảnh trên",
    "theo ngữ cảnh trên",
    "theo tài liệu trên",
    "trong đoạn văn trên",
    "according to the passage",
    "according to the text",
    "based on the context",
    "in the passage above",
)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)


def _get_value(source: Any, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if isinstance(source, dict) and key in source:
            return source[key]
        if hasattr(source, key):
            return getattr(source, key)
    return default


def _text(value: Any) -> str:
    return str(value or "").strip()


def _option_text(option: Any) -> str:
    return _text(_get_value(option, "text", "content", default=""))


def _option_is_correct(option: Any) -> bool:
    return bool(_get_value(option, "is_correct", default=False))


def _questions_from_batch_or_iterable(batch: Any) -> list[Any]:
    if isinstance(batch, GeneratedQuestionBatch):
        return list(batch.questions)
    if isinstance(batch, dict) and "questions" in batch:
        return list(batch["questions"])
    if hasattr(batch, "questions"):
        return list(getattr(batch, "questions"))
    return list(batch)


def _contains_any(text: str, phrases: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def validate_question(
    question: Any,
    *,
    allowed_chunk_ids: Iterable[int] | None = None,
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    scores: dict[str, float] = {}

    question_text = _text(_get_value(question, "question_text", "content", default=""))
    options = list(_get_value(question, "options", default=[]) or [])
    correct_answer = _text(_get_value(question, "correct_answer", default=""))
    difficulty = _text(_get_value(question, "difficulty", default="")).lower()
    bloom_level = _text(_get_value(question, "bloom_level", default="")).lower()
    explanation = _text(_get_value(question, "explanation", default=""))
    source_chunk_ids = list(_get_value(question, "source_chunk_ids", default=[]) or [])

    # -- hợp đồng MCQ (errors) ------------------------------------------

    if not question_text:
        errors.append("question_text/content must not be empty")

    if len(options) != 4:
        errors.append("MCQ must have exactly 4 options")

    option_texts = [_option_text(option) for option in options]
    if any(not text for text in option_texts):
        errors.append("all options must have non-empty text/content")

    normalized_options = [text.lower() for text in option_texts if text]
    if len(set(normalized_options)) != len(normalized_options):
        errors.append("all options must be distinct")

    correct_options = [option for option in options if _option_is_correct(option)]
    if len(correct_options) != 1:
        errors.append("MCQ must have exactly 1 correct option")
    elif correct_answer and _option_text(correct_options[0]) != correct_answer:
        errors.append("correct_answer must match the correct option text")

    if not correct_answer:
        errors.append("correct_answer must not be empty")

    if not explanation:
        errors.append("explanation must not be empty")

    if difficulty not in DIFFICULTY_LEVELS:
        errors.append("difficulty must be one of easy, medium, hard")

    if bloom_level not in BLOOM_LEVELS:
        errors.append(
            "bloom_level must be one of remember, understand, apply, analyze, evaluate, create"
        )

    # -- chất lượng (warnings) ------------------------------------------

    if not source_chunk_ids:
        warnings.append("source_chunk_ids is empty")
    elif allowed_chunk_ids is not None:
        allowed = {int(chunk_id) for chunk_id in allowed_chunk_ids}
        unknown = [
            chunk_id for chunk_id in source_chunk_ids if int(chunk_id) not in allowed
        ]
        if unknown:
            warnings.append(
                f"source_chunk_ids ngoài context: {unknown}"
            )

    if question_text and len(question_text) < MIN_QUESTION_TEXT_LENGTH:
        warnings.append("question_text quá ngắn, có thể thiếu ngữ cảnh")

    if explanation and len(explanation) < MIN_EXPLANATION_LENGTH:
        warnings.append("explanation quá ngắn để giải thích đáp án")

    if question_text and _contains_any(question_text, SELF_REFERENCE_PHRASES):
        warnings.append("question_text tham chiếu ngược vào tài liệu, không đứng độc lập")

    if any(_contains_any(text, BANNED_OPTION_PHRASES) for text in option_texts):
        warnings.append("có phương án dạng 'tất cả/không đáp án nào ở trên'")

    if len(correct_options) == 1 and len(option_texts) == 4:
        correct_length = len(_option_text(correct_options[0]))
        distractor_lengths = [
            len(text)
            for option, text in zip(options, option_texts)
            if not _option_is_correct(option)
        ]
        longest_distractor = max(distractor_lengths, default=0)
        if longest_distractor and correct_length > MAX_CORRECT_LENGTH_RATIO * longest_distractor:
            warnings.append("đáp án đúng dài hơn hẳn các phương án nhiễu, dễ lộ đáp án")

    scores["format"] = 1.0 if not errors else 0.0
    scores["grounding"] = 1.0 if source_chunk_ids else 0.5
    scores["quality"] = max(0.0, 1.0 - 0.2 * len(warnings)) if not errors else 0.0

    return ValidationResult(
        is_valid=not errors,
        errors=errors,
        warnings=warnings,
        scores=scores,
    )


def validate_questions(
    batch: Any,
    *,
    allowed_chunk_ids: Iterable[int] | None = None,
) -> list[ValidationResult]:
    allowed = list(allowed_chunk_ids) if allowed_chunk_ids is not None else None
    return [
        validate_question(question, allowed_chunk_ids=allowed)
        for question in _questions_from_batch_or_iterable(batch)
    ]


__all__ = ["ValidationResult", "validate_question", "validate_questions"]
