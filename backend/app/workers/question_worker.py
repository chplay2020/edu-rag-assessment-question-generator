import logging
from datetime import datetime, timezone
from typing import cast

from sqlalchemy.orm import Session

from app.ai import pipeline
from app.ai.embedding.embedder import embed_texts, is_semantic_embedding_enabled
from app.ai.generation import question_generator  # noqa: F401  (điểm mock của test/pipeline)
from app.ai.retrieval import retriever  # noqa: F401  (điểm mock của test/pipeline)
from app.ai.validation import question_validator  # noqa: F401  (điểm mock của test/pipeline)
from app.ai.vector_store.qdrant_store import QuestionVector, get_vector_store
from app.core.database import SessionLocal
from app.models.material import Job, Material
from app.models.question import Option, Question


logger = logging.getLogger(__name__)


class QuestionGenerationError(Exception):
    pass


def _set_job_status(db: Session, job: Job, status: str) -> None:
    job.status = status
    if status in {"done", "failed"}:
        job.finished_at = datetime.now(timezone.utc)
    db.add(job)


def _index_questions(questions: list[Question], material_id: int, course_id: int) -> None:
    """Đẩy câu hỏi vừa lưu vào collection question_vectors.

    Nhờ bước này, lần sinh sau có thể phát hiện trùng với toàn bộ ngân hàng
    câu hỏi. Lỗi ở đây không được làm hỏng job vì câu hỏi đã lưu DB thành công.
    """
    if not questions or not is_semantic_embedding_enabled():
        return

    try:
        vectors = embed_texts([cast(str, question.content) for question in questions])
        store = get_vector_store()
        store.ensure_collections()
        store.upsert_question_vectors(
            [
                QuestionVector(
                    question_id=cast(int, question.id),
                    material_id=material_id,
                    course_id=course_id,
                    content=cast(str, question.content),
                    difficulty=cast(str | None, question.difficulty),
                    bloom_level=cast(str | None, question.bloom_level),
                    status=cast(str | None, question.status),
                )
                for question in questions
            ],
            vectors,
        )
    except Exception as exc:
        logger.warning(
            "Không index được câu hỏi vào Qdrant (material_id=%s): %s", material_id, exc
        )


def process_question_generation_job(
    job_id: int,
    *,
    query: str | None = None,
    number_of_questions: int = 5,
    difficulty: str = "medium",
    bloom_level: str | None = None,
    language: str = "vi",
    top_k: int = 5,
) -> None:
    db: Session = SessionLocal()
    job: Job | None = None

    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise QuestionGenerationError(f"Job not found: {job_id}")
        if cast(str, job.task_type) != "generate_questions":
            raise QuestionGenerationError(
                f"Job {job_id} is not a generate_questions job."
            )

        _set_job_status(db, job, "running")
        db.commit()
        db.refresh(job)

        material = db.query(Material).filter(Material.id == job.material_id).first()
        if not material:
            raise QuestionGenerationError(
                f"Material not found for question generation job: {job_id}"
            )
        if cast(str, material.status) != "processed":
            raise QuestionGenerationError(
                f"Material {material.id} must be processed before question generation."
            )

        material_id = cast(int, material.id)
        course_id = cast(int, material.course_id)
        retrieval_query = (query or cast(str, material.title)).strip()
        if not retrieval_query:
            retrieval_query = f"material {material_id}"

        outcome = pipeline.generate_questions_for_material(
            material_id=material_id,
            course_id=course_id,
            query=retrieval_query,
            number_of_questions=number_of_questions,
            difficulty=difficulty,
            bloom_level=bloom_level,
            language=language,
            top_k=top_k,
        )

        for warning in outcome.warnings:
            logger.warning("Job %s: %s", job_id, warning)
        for dropped in outcome.dropped:
            logger.info("Job %s loại bỏ câu hỏi: %s", job_id, dropped)

        if not outcome.candidates:
            raise QuestionGenerationError(
                f"Không có câu hỏi hợp lệ nào cho job {job_id}. "
                f"Đã loại bỏ {len(outcome.dropped)} câu: "
                + ("; ".join(outcome.dropped[:3]) or "không rõ nguyên nhân")
            )

        saved_questions: list[Question] = []
        for candidate in outcome.candidates:
            generated_question = candidate.question
            question = Question(
                material_id=material_id,
                course_id=course_id,
                job_id=job_id,
                content=generated_question.question_text,
                difficulty=generated_question.difficulty,
                bloom_level=generated_question.bloom_level,
                question_type="multiple_choice",
                explanation=generated_question.explanation,
                status=candidate.status,
                source_chunk_ids=generated_question.source_chunk_ids,
            )
            setattr(
                question,
                "options",
                [
                    Option(content=option.text, is_correct=option.is_correct)
                    for option in generated_question.options
                ],
            )
            db.add(question)
            saved_questions.append(question)

        _set_job_status(db, job, "done")
        db.commit()

        _index_questions(saved_questions, material_id, course_id)

    except Exception:
        db.rollback()
        if job is not None:
            _set_job_status(db, job, "failed")
            db.commit()
        raise
    finally:
        db.close()


__all__ = ["QuestionGenerationError", "process_question_generation_job"]
