from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.question import Question

APPROVED_STATUS = "approved"


def get_question_bank(
    db: Session,
    *,
    course_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    bloom_level: Optional[str] = None,
    question_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Question]:
    """
    Lấy danh sách câu hỏi đã được duyệt (status='approved').
    Các filter đều optional, có thể kết hợp.
    Sắp xếp theo created_at giảm dần (mới nhất trước).
    """
    query = db.query(Question).filter(Question.status == APPROVED_STATUS)

    if course_id is not None:
        query = query.filter(Question.course_id == course_id)

    if difficulty is not None:
        query = query.filter(Question.difficulty == difficulty)

    if bloom_level is not None:
        query = query.filter(Question.bloom_level == bloom_level)

    if question_type is not None:
        query = query.filter(Question.question_type == question_type)

    return (
        query
        .order_by(Question.created_at.desc(), Question.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
