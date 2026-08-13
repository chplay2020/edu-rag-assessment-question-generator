from dataclasses import dataclass, field
from typing import Any

from app.ai.generation.output_parser import GeneratedQuestionBatch
from app.ai.validation.bloom_classifier import BLOOM_LEVELS, DIFFICULTY_LEVELS


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


def validate_question(question: Any) -> ValidationResult:
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

    if not question_text:
        errors.append("question_text/content must not be empty")

    if len(options) != 4:
        errors.append("MCQ must have exactly 4 options")

    option_texts = [_option_text(option) for option in options]
    if any(not text for text in option_texts):
        errors.append("all options must have non-empty text/content")

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

    if not source_chunk_ids:
        warnings.append("source_chunk_ids is empty")

    scores["format"] = 1.0 if not errors else 0.0
    scores["grounding"] = 1.0 if source_chunk_ids else 0.5

    return ValidationResult(
        is_valid=not errors,
        errors=errors,
        warnings=warnings,
        scores=scores,
    )


def validate_questions(batch: Any) -> list[ValidationResult]:
    return [validate_question(question) for question in _questions_from_batch_or_iterable(batch)]


__all__ = ["ValidationResult", "validate_question", "validate_questions"]
