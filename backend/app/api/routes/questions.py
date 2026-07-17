from fastapi import APIRouter
from typing import List, Any
from app.schemas.question_schema import QuestionCreate, QuestionUpdate, QuestionResponse, ReviewCreate, ReviewResponse
from datetime import datetime

router = APIRouter()

@router.get("/material/{material_id}", response_model=List[QuestionResponse])
def get_questions_by_material(material_id: int) -> Any:
    """Lấy danh sách câu hỏi theo tài liệu"""
    return [
        QuestionResponse(
            id=1, material_id=material_id, course_id=1,
            content="What is Python?", difficulty_level=1,
            blooms_taxonomy="remember", status="pending",
            created_at=datetime.now(), updated_at=datetime.now(),
            options=[
                {"id": 1, "question_id": 1, "content": "A snake", "is_correct": False},
                {"id": 2, "question_id": 1, "content": "A programming language", "is_correct": True}
            ]
        )
    ]

@router.post("/", response_model=QuestionResponse)
def create_question(data: QuestionCreate) -> Any:
    """Thêm câu hỏi thủ công"""
    return QuestionResponse(
        id=2, material_id=data.material_id, course_id=data.course_id,
        content=data.content, difficulty_level=data.difficulty_level,
        blooms_taxonomy=data.blooms_taxonomy, status="approved",
        created_at=datetime.now(), updated_at=datetime.now(),
        options=[{"id": 3, "question_id": 2, "content": opt.content, "is_correct": opt.is_correct} for opt in data.options]
    )

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, data: QuestionUpdate) -> Any:
    """Sửa đổi câu hỏi"""
    return QuestionResponse(
        id=question_id, material_id=1, course_id=1,
        content=data.content or "Updated content", difficulty_level=data.difficulty_level or 1,
        blooms_taxonomy=data.blooms_taxonomy, status=data.status or "pending",
        created_at=datetime.now(), updated_at=datetime.now(),
        options=[]
    )

@router.post("/{question_id}/review", response_model=ReviewResponse)
def review_question(question_id: int, data: ReviewCreate) -> Any:
    """Giảng viên đánh giá (Duyệt/Bỏ) câu hỏi"""
    return ReviewResponse(
        id=1, question_id=question_id, reviewer_id=1,
        action=data.action, comments=data.comments,
        created_at=datetime.now()
    )
