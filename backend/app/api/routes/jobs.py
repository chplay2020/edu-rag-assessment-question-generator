from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Annotated, Any, cast, List, Optional
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_id, get_current_user_role, get_current_active_lecturer
from app.models.material import Job
from app.schemas.material_schema import JobResponse
from app.models.question import Question
from app.schemas.question_schema import QuestionResponse
from app.services import course_service, question_generation_service
from app.workers.question_worker import process_question_generation_job

router = APIRouter()


class GenerateQuestionsRequest(BaseModel):
    """Body schema cho endpoint sinh câu hỏi.
    Frontend gửi JSON body với các field này.
    """
    query: Optional[str] = Field(default=None, description="Yêu cầu bổ sung hoặc phạm vi sinh câu hỏi")
    number_of_questions: int = Field(default=5, ge=1, le=50, description="Số lượng câu hỏi cần sinh")
    difficulty: str = Field(default="medium", description="Độ khó: easy | medium | hard")
    bloom_level: Optional[str] = Field(default=None, description="Mức độ nhận thức Bloom")
    language: str = Field(default="vi", description="Ngôn ngữ: vi | en")
    top_k: int = Field(default=5, ge=1, le=20, description="Số lượng chunk retrieval")


@router.post(
    "/material/{material_id}/generate-questions",
    response_model=JobResponse,
    dependencies=[Depends(get_current_active_lecturer)],
)
def generate_questions_for_material(
    material_id: int,
    body: GenerateQuestionsRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
) -> Any:
    """Tạo job sinh câu hỏi cho material đã processed.

    Nhận JSON body với các tham số sinh câu hỏi.
    Trả về JobResponse (với id, status, ...) để frontend điều hướng đúng.
    """
    job = question_generation_service.create_question_generation_job(
        db=db,
        material_id=material_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
        config={
            "query": body.query,
            "number_of_questions": body.number_of_questions,
            "difficulty": body.difficulty,
            "bloom_level": body.bloom_level,
            "language": body.language,
            "top_k": body.top_k,
        }
    )
    background_tasks.add_task(
        process_question_generation_job,
        cast(int, job.id),
        query=body.query,
        number_of_questions=body.number_of_questions,
        difficulty=body.difficulty,
        bloom_level=body.bloom_level,
        language=body.language,
        top_k=body.top_k,
    )
    return job


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

@router.get("/{job_id}/questions", response_model=List[QuestionResponse], dependencies=[Depends(get_current_active_lecturer)])
def get_job_questions(
    job_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Lấy danh sách câu hỏi được sinh ra từ một job."""
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

    return db.query(Question).filter(Question.job_id == job_id).all()
