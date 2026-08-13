from datetime import datetime, timezone
from typing import cast

from sqlalchemy.orm import Session

from app.ai.generation import question_generator
from app.ai.retrieval import retriever
from app.ai.validation import question_validator
from app.core.database import SessionLocal
from app.models.material import Job, Material
from app.models.question import Option, Question


class QuestionGenerationError(Exception):
    pass


def _set_job_status(db: Session, job: Job, status: str) -> None:
    job.status = status
    if status in {"done", "failed"}:
        job.finished_at = datetime.now(timezone.utc)
    db.add(job)


def _question_status_for_validation(
    validation_result: question_validator.ValidationResult,
) -> str:
    return "review_required" if validation_result.warnings else "draft"


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

        context_chunks = retriever.retrieve_context(
            retrieval_query,
            material_id=material_id,
            course_id=course_id,
            top_k=top_k,
        )
        generated_batch = question_generator.generate_questions(
            context_chunks=context_chunks,
            material_id=material_id,
            course_id=course_id,
            number_of_questions=number_of_questions,
            difficulty=difficulty,
            bloom_level=bloom_level,
            language=language,
        )
        validation_results = question_validator.validate_questions(generated_batch)
        invalid_results = [result for result in validation_results if not result.is_valid]
        if invalid_results:
            first_errors = "; ".join(invalid_results[0].errors)
            raise QuestionGenerationError(
                f"Generated question validation failed: {first_errors}"
            )

        for generated_question, validation_result in zip(
            generated_batch.questions,
            validation_results,
            strict=True,
        ):
            question = Question(
                material_id=material_id,
                course_id=course_id,
                content=generated_question.question_text,
                difficulty=generated_question.difficulty,
                bloom_level=generated_question.bloom_level,
                question_type="multiple_choice",
                explanation=generated_question.explanation,
                status=_question_status_for_validation(validation_result),
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

        _set_job_status(db, job, "done")
        db.commit()

    except Exception:
        db.rollback()
        if job is not None:
            _set_job_status(db, job, "failed")
            db.commit()
        raise
    finally:
        db.close()


__all__ = ["QuestionGenerationError", "process_question_generation_job"]
