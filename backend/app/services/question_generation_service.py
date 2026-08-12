from typing import Any, cast

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.material import Job, Material
from app.services import course_service


def create_question_generation_job(
    *,
    db: Session,
    material_id: int,
    current_user_id: int,
    current_user_role: str,
    config: dict[str, Any] | None = None,
) -> Job:
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài liệu không tồn tại.",
        )

    course = course_service.get_course(
        db=db,
        course_id=cast(int, material.course_id),
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài liệu không tồn tại hoặc bạn không có quyền truy cập.",
        )

    if cast(str, material.status) != "processed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chỉ có thể sinh câu hỏi khi tài liệu đã processed.",
        )

    job = Job(
        material_id=material_id,
        task_type="generate_questions",
        status="pending",
        config=config,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def job_summary(job: Job) -> dict[str, Any]:
    return {
        "job_id": cast(int, job.id),
        "material_id": cast(int, job.material_id),
        "task_type": cast(str, job.task_type),
        "job_status": cast(str, job.status),
        "config": cast(dict[str, Any] | None, job.config),
    }


__all__ = ["create_question_generation_job", "job_summary"]
