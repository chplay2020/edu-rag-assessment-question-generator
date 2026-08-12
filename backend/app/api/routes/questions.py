from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any, cast
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_id, get_current_user_role, get_current_active_lecturer
from app.models.material import Material
from app.models.question import Question, Option, Review
from app.schemas.question_schema import QuestionCreate, QuestionUpdate, QuestionResponse, ReviewCreate, ReviewResponse
from app.services import course_service

router = APIRouter()

QUESTION_STATUSES = {"draft", "review_required", "approved", "rejected"}
CREATE_STATUSES = {"draft", "review_required"}
REVIEW_STATUSES = {"approved", "rejected"}


def _get_material_with_access(
    db: Session,
    material_id: int,
    current_user_id: int,
    current_user_role: str,
) -> Material:
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài liệu không tồn tại."
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
            detail="Tài liệu không tồn tại hoặc bạn không có quyền truy cập."
        )
    return material


def _get_question_with_access(
    db: Session,
    question_id: int,
    current_user_id: int,
    current_user_role: str,
) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu hỏi không tồn tại."
        )

    course = course_service.get_course(
        db=db,
        course_id=cast(int, question.course_id),
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu hỏi không tồn tại hoặc bạn không có quyền truy cập."
        )
    return question


@router.get("/material/{material_id}", response_model=List[QuestionResponse], dependencies=[Depends(get_current_active_lecturer)])
def get_questions_by_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Lấy danh sách câu hỏi theo tài liệu"""
    _get_material_with_access(
        db=db,
        material_id=material_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    return (
        db.query(Question)
        .filter(Question.material_id == material_id)
        .order_by(Question.created_at.desc())
        .all()
    )

@router.post("/", response_model=QuestionResponse, dependencies=[Depends(get_current_active_lecturer)])
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Thêm câu hỏi thủ công"""
    material = _get_material_with_access(
        db=db,
        material_id=data.material_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    if cast(int, material.course_id) != data.course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material không thuộc khóa học đã chọn."
        )
    if data.status not in CREATE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Câu hỏi mới chỉ được tạo ở trạng thái draft hoặc review_required."
        )

    question = Question(
        material_id=data.material_id,
        course_id=data.course_id,
        content=data.content,
        difficulty=data.difficulty,
        bloom_level=data.bloom_level,
        question_type=data.question_type,
        explanation=data.explanation,
        source_chunk_ids=data.source_chunk_ids,
        status=data.status,
    )
    setattr(
        question,
        "options",
        [
            Option(content=option.content, is_correct=option.is_correct)
            for option in data.options
        ],
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.put("/{question_id}", response_model=QuestionResponse, dependencies=[Depends(get_current_active_lecturer)])
def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Sửa đổi câu hỏi"""
    question = _get_question_with_access(
        db=db,
        question_id=question_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] not in QUESTION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trạng thái câu hỏi không hợp lệ."
        )
    for field, value in update_data.items():
        setattr(question, field, value)

    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.post("/{question_id}/review", response_model=ReviewResponse, dependencies=[Depends(get_current_active_lecturer)])
def review_question(
    question_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Giảng viên đánh giá (Duyệt/Bỏ) câu hỏi"""
    question = _get_question_with_access(
        db=db,
        question_id=question_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    if data.status not in REVIEW_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review chỉ hỗ trợ approved hoặc rejected."
        )

    review = Review(
        question_id=question_id,
        reviewed_by=current_user_id,
        status=data.status,
        feedback=data.feedback,
    )
    setattr(question, "status", data.status)
    db.add(review)
    db.add(question)
    db.commit()
    db.refresh(review)
    return review
