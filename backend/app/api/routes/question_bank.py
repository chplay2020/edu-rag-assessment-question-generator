from __future__ import annotations
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_lecturer
from app.schemas.question_schema import QuestionResponse
from app.services import question_bank_service

router = APIRouter()

@router.get(
    "/bank",
    response_model=List[QuestionResponse],
    summary="Question Bank – Danh sách câu hỏi đã duyệt",
    description=(
        "Trả về danh sách câu hỏi có status='approved'. "
        "Hỗ trợ filter theo course_id, difficulty, bloom_level, question_type và phân trang."
    ),
    dependencies=[Depends(get_current_active_lecturer)],
)
def get_question_bank(
    db: Session = Depends(get_db),
    course_id: Optional[int] = Query(default=None, description="Lọc theo môn học"),
    difficulty: Optional[str] = Query(default=None, description="easy | medium | hard"),
    bloom_level: Optional[str] = Query(default=None, description="Bloom taxonomy level"),
    question_type: Optional[str] = Query(default=None, description="multiple_choice | ..."),
    skip: int = Query(default=0, ge=0, description="Số bản ghi bỏ qua (phân trang)"),
    limit: int = Query(default=20, ge=1, le=200, description="Số bản ghi tối đa trả về"),
) -> Any:
    """Lấy danh sách câu hỏi đã được duyệt (Question Bank)."""
    return question_bank_service.get_question_bank(
        db=db,
        course_id=course_id,
        difficulty=difficulty,
        bloom_level=bloom_level,
        question_type=question_type,
        skip=skip,
        limit=limit,
    )
