from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, cast
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_id, get_current_user_role, get_current_active_lecturer
from app.models.material import Job
from app.schemas.material_schema import JobResponse
from app.services import course_service

router = APIRouter()

@router.get("/{job_id}", response_model=JobResponse, dependencies=[Depends(get_current_active_lecturer)])
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Kiểm tra trạng thái job xử lý material hoặc sinh câu hỏi."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job không tồn tại."
        )

    course = course_service.get_course(
        db=db,
        course_id=cast(int, job.material.course_id),
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job không tồn tại hoặc bạn không có quyền truy cập."
        )

    return job
