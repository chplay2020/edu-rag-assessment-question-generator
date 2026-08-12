from datetime import datetime, timezone
from typing import cast

from sqlalchemy.orm import Session

from app.ai.chunking.chunker import chunk_text
from app.ai.extraction.pdf_extractor import extract_and_save_raw_text
from app.ai.extraction.text_cleaner import clean_and_save_text
from app.core.database import SessionLocal
from app.models.material import Chunk, Job, Material


PROCESSABLE_STATUSES = {"uploaded", "failed"}


class MaterialProcessingError(Exception):
    pass


def _latest_process_job(db: Session, material_id: int) -> Job | None:
    return (
        db.query(Job)
        .filter(
            Job.material_id == material_id,
            Job.task_type == "process_material",
            Job.status.in_(["pending", "running"]),
        )
        .order_by(Job.created_at.desc(), Job.id.desc())
        .first()
    )


def _set_job_status(db: Session, job: Job | None, status: str) -> None:
    if not job:
        return
    job.status = status
    if status in {"done", "failed"}:
        job.finished_at = datetime.now(timezone.utc)
    db.add(job)


def process_material(material_id: int) -> None:
    db: Session = SessionLocal()
    material: Material | None = None
    job: Job | None = None
    processing_started = False

    try:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise MaterialProcessingError(f"Material not found: {material_id}")

        current_status = cast(str, material.status)
        if current_status not in PROCESSABLE_STATUSES:
            raise MaterialProcessingError(
                f"Material {material_id} cannot be processed from status '{current_status}'."
            )

        job = _latest_process_job(db, material_id)
        material.status = "processing"
        _set_job_status(db, job, "running")
        db.add(material)
        db.commit()
        db.refresh(material)
        processing_started = True

        raw_text, _raw_path = extract_and_save_raw_text(
            material_id=material_id,
            file_path=cast(str, material.file_path),
        )
        cleaned_text, _clean_path = clean_and_save_text(material_id, raw_text)
        chunks = chunk_text(cleaned_text)

        db.query(Chunk).filter(Chunk.material_id == material_id).delete(
            synchronize_session=False
        )
        for chunk in chunks:
            db.add(
                Chunk(
                    material_id=material_id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                )
            )

        material.status = "processed"
        _set_job_status(db, job, "done")
        db.add(material)
        db.commit()

    except Exception:
        db.rollback()
        if material is not None and processing_started:
            material.status = "failed"
            db.add(material)
        if processing_started:
            _set_job_status(db, job, "failed")
        db.commit()
        raise
    finally:
        db.close()


__all__ = ["MaterialProcessingError", "process_material"]
