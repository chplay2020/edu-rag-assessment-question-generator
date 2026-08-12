from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from typing import Annotated, Any, cast
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_id, get_current_user_role, get_current_active_lecturer
from app.models.material import Job
from app.schemas.material_schema import JobResponse
from app.services import course_service, question_generation_service
from app.workers.question_worker import process_question_generation_job

router = APIRouter()


@router.post("/material/{material_id}/generate-questions", dependencies=[Depends(get_current_active_lecturer)])
def generate_questions_for_material(
    material_id: int,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
    query: str | None = None,
    number_of_questions: int = Query(default=5, ge=1, le=50),
    difficulty: str = "medium",
    bloom_level: str | None = None,
    language: str = "vi",
    top_k: int = Query(default=5, ge=1, le=20),
) -> dict[str, Any]:
    """Tạo job sinh câu hỏi cho material đã processed."""
    job = question_generation_service.create_question_generation_job(
        db=db,
        material_id=material_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    background_tasks.add_task(
        process_question_generation_job,
        cast(int, job.id),
        query=query,
        number_of_questions=number_of_questions,
        difficulty=difficulty,
        bloom_level=bloom_level,
        language=language,
        top_k=top_k,
    )
    return question_generation_service.job_summary(job)


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
