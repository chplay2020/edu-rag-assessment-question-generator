"""Orchestrator của luồng sinh câu hỏi.

Toàn bộ thứ tự bước nằm ở đây, worker chỉ còn việc lưu DB. Nhờ vậy luồng AI
có thể test và chỉnh riêng, không lẫn với logic job/transaction.

    retrieve (multi-query + diversity)
    -> generate (Gemini JSON mode, sinh bù khi thiếu)
    -> refine nhãn Bloom/difficulty
    -> validate bằng luật
    -> loại trùng trong lô
    -> loại trùng với ngân hàng câu hỏi
    -> LLM judge (tuỳ chọn)
    -> gán trạng thái draft / review_required

Nguyên tắc: chỉ lỗi khiến không còn câu hỏi nào mới làm fail job. Mọi bước
phụ trợ (dedupe, judge) hỏng thì ghi cảnh báo và đi tiếp.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from app.ai.embedding.embedder import is_semantic_embedding_enabled
from app.ai.generation import question_generator
from app.ai.generation.output_parser import GeneratedQuestion
from app.ai.retrieval import retriever
from app.ai.validation import bloom_classifier, duplicate_detector, question_validator
from app.ai.validation.llm_judge import JudgeVerdict, is_judge_enabled, judge_questions
from app.core.config import settings


logger = logging.getLogger(__name__)

STATUS_DRAFT = "draft"
STATUS_REVIEW_REQUIRED = "review_required"


@dataclass
class QuestionCandidate:
    question: GeneratedQuestion
    status: str
    validation: question_validator.ValidationResult
    judge: JudgeVerdict | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class GenerationOutcome:
    candidates: list[QuestionCandidate] = field(default_factory=list)
    context_chunks: list[Any] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ai_logs: list[dict[str, Any]] = field(default_factory=list)

    @property
    def questions(self) -> list[GeneratedQuestion]:
        return [candidate.question for candidate in self.candidates]


def _allowed_chunk_ids(context_chunks: list[Any]) -> list[int]:
    ids: list[int] = []
    for chunk in context_chunks:
        chunk_id = (
            chunk.get("chunk_id") if isinstance(chunk, dict) else getattr(chunk, "chunk_id", None)
        )
        if chunk_id is not None:
            ids.append(int(chunk_id))
    return ids


def _refine(question: GeneratedQuestion) -> GeneratedQuestion:
    """Chuẩn hoá nhãn difficulty/bloom về đúng danh mục."""
    difficulty, bloom_level = bloom_classifier.refine_labels(
        question.question_text,
        difficulty=question.difficulty,
        bloom_level=question.bloom_level,
    )
    if difficulty == question.difficulty and bloom_level == question.bloom_level:
        return question
    return question.model_copy(update={"difficulty": difficulty, "bloom_level": bloom_level})


def _grounding_warnings(
    question: GeneratedQuestion,
    allowed_chunk_ids: list[int],
) -> list[str]:
    """Cảnh báo khi câu hỏi trích dẫn chunk không có trong context.

    Việc kiểm tra này nằm ở pipeline (không nằm trong `validate_questions`) để
    tầng validate giữ nguyên chữ ký một tham số, dễ mock và dùng lại cho câu
    hỏi nhập tay - vốn không có context kèm theo.
    """
    if not allowed_chunk_ids:
        return []
    allowed = set(allowed_chunk_ids)
    unknown = [chunk_id for chunk_id in question.source_chunk_ids if chunk_id not in allowed]
    if not unknown:
        return []
    return [f"source_chunk_ids ngoài context: {unknown}"]


def _check_question_bank_duplicate(
    question: GeneratedQuestion,
    *,
    material_id: int,
    course_id: int,
) -> tuple[bool, list[str]]:
    result = duplicate_detector.detect_duplicate_question(
        question.question_text,
        material_id=material_id,
        course_id=course_id,
    )
    return result.is_duplicate, result.warnings


def generate_questions_for_material(
    *,
    material_id: int,
    course_id: int,
    query: str,
    number_of_questions: int = 5,
    difficulty: str = "medium",
    bloom_level: str | None = None,
    language: str = "vi",
    top_k: int | None = None,
    check_duplicates: bool = True,
) -> GenerationOutcome:
    outcome = GenerationOutcome()

    # Với embedding giả, điểm similarity vô nghĩa nên kiểm tra trùng theo
    # vector chỉ tạo nhiễu (và một lần gọi Qdrant vô ích).
    if check_duplicates and not is_semantic_embedding_enabled():
        check_duplicates = False
        outcome.warnings.append(
            "Bỏ qua kiểm tra trùng theo vector vì EMBEDDING_PROVIDER không phải Gemini."
        )

    # 1. Retrieval
    context_chunks = retriever.retrieve_diverse_context(
        query,
        material_id=material_id,
        course_id=course_id,
        top_k=top_k or settings.RAG_TOP_K,
        language=language,
    )
    outcome.context_chunks = list(context_chunks)
    if not context_chunks:
        outcome.warnings.append(
            "Không lấy được chunk nào từ vector store; câu hỏi sẽ thiếu ngữ liệu."
        )
        logger.warning(
            "Retrieval rỗng cho material_id=%s course_id=%s query=%r",
            material_id,
            course_id,
            query,
        )

    allowed_chunk_ids = _allowed_chunk_ids(list(context_chunks))

    # 2. Generation (đã bao gồm parse + sinh bù bên trong)
    batch = question_generator.generate_questions(
        context_chunks=list(context_chunks),
        material_id=material_id,
        course_id=course_id,
        number_of_questions=number_of_questions,
        difficulty=difficulty,
        bloom_level=bloom_level,
        language=language,
    )
    outcome.ai_logs.extend(batch.logs)

    # 3. Refine nhãn + 4. validate bằng luật
    refined = [_refine(question) for question in batch.questions]
    validations = question_validator.validate_questions(refined)

    kept: list[tuple[GeneratedQuestion, question_validator.ValidationResult]] = []
    for question, validation in zip(refined, validations, strict=True):
        validation.warnings.extend(_grounding_warnings(question, allowed_chunk_ids))
        if validation.is_valid:
            kept.append((question, validation))
        else:
            outcome.dropped.append(
                f"{question.question_text[:80]} -> {'; '.join(validation.errors)}"
            )

    # 5. Loại trùng ngay trong lô
    duplicate_indexes = duplicate_detector.find_near_duplicates_in_batch(
        [question.question_text for question, _ in kept]
    )
    if duplicate_indexes:
        for index in sorted(duplicate_indexes):
            outcome.dropped.append(
                f"{kept[index][0].question_text[:80]} -> trùng với câu hỏi khác trong cùng lô"
            )
        kept = [item for index, item in enumerate(kept) if index not in duplicate_indexes]

    # 6. LLM judge (một lần gọi cho cả lô)
    verdicts: dict[int, JudgeVerdict] = {}
    if kept and is_judge_enabled():
        verdicts = judge_questions(
            [question for question, _ in kept],
            context_text=retriever.build_context_text(list(context_chunks)),
        )

    # 7. Trùng với ngân hàng câu hỏi + gán trạng thái
    for index, (question, validation) in enumerate(kept):
        notes: list[str] = []
        needs_review = bool(validation.warnings)

        verdict = verdicts.get(index)
        if verdict is not None:
            if not verdict.is_valid:
                outcome.dropped.append(
                    f"{question.question_text[:80]} -> judge từ chối: {'; '.join(verdict.errors)}"
                )
                continue
            notes.extend(verdict.warnings)
            if verdict.warnings or verdict.average_score < settings.LLM_JUDGE_MIN_SCORE:
                needs_review = True

        if check_duplicates:
            is_duplicate, duplicate_warnings = _check_question_bank_duplicate(
                question,
                material_id=material_id,
                course_id=course_id,
            )
            outcome.warnings.extend(duplicate_warnings)
            if is_duplicate:
                notes.append("Có thể trùng với câu hỏi đã duyệt trong ngân hàng.")
                needs_review = True

        outcome.candidates.append(
            QuestionCandidate(
                question=question,
                status=STATUS_REVIEW_REQUIRED if needs_review else STATUS_DRAFT,
                validation=validation,
                judge=verdict,
                notes=notes,
            )
        )

    logger.info(
        "Pipeline xong: material_id=%s yêu cầu=%s giữ lại=%s loại bỏ=%s chunk=%s",
        material_id,
        number_of_questions,
        len(outcome.candidates),
        len(outcome.dropped),
        len(outcome.context_chunks),
    )
    return outcome


__all__ = [
    "GenerationOutcome",
    "QuestionCandidate",
    "STATUS_DRAFT",
    "STATUS_REVIEW_REQUIRED",
    "generate_questions_for_material",
]
