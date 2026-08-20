from __future__ import annotations
from typing import List, Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.question import Question
from app.models.course import Course
from app.models.user import User

APPROVED_STATUS = "approved"


def _base_approved_query(db: Session):
    """Query cơ sở: chỉ câu hỏi có status='approved', course chưa bị xóa."""
    return (
        db.query(Question)
        .join(Course, Course.id == Question.course_id)
        .filter(Question.status == APPROVED_STATUS)
        .filter(Course.is_deleted == False)  # noqa: E712
    )


def _apply_ownership_filter(query, current_user: User):
    if current_user.role == "admin":
        return query
    return query.filter(Course.created_by == current_user.id)


def get_question_bank(
    db: Session,
    *,
    current_user: User,
    course_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    bloom_level: Optional[str] = None,
    question_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Question]:

    query = _base_approved_query(db)
    query = _apply_ownership_filter(query, current_user)

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


from sqlalchemy.orm import selectinload, joinedload

def get_exportable_questions(
    db: Session,
    *,
    current_user: User,
    question_ids: Sequence[int],
    with_relations: bool = False,
) -> List[Question]:

    if not question_ids:
        return []

    unique_ids = list(set(question_ids))

    query = _base_approved_query(db)
    query = _apply_ownership_filter(query, current_user)
    query = query.filter(Question.id.in_(unique_ids))
    
    if with_relations:
        query = query.options(selectinload(Question.options), joinedload(Question.material))

    found: List[Question] = query.all()
    found_ids = {q.id for q in found}
    invalid_ids = sorted(set(unique_ids) - found_ids)

    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": (
                    "Một hoặc nhiều câu hỏi không đủ điều kiện export "
                    "(không tồn tại, chưa được duyệt, hoặc không thuộc môn học của bạn)."
                ),
                "invalid_question_ids": invalid_ids,
            },
        )

    return found
