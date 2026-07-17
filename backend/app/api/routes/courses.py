from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user_id,
    get_current_user_role,
    get_db,
)
from app.schemas.course_schema import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)
from app.services import course_service

router = APIRouter()

# Mô tả phản hồi lỗi 404 trong tài liệu OpenAPI/Swagger.
not_found_response = {
    "description": "Course not found",
    "content": {
        "application/json": {
            "example": {
                "message": "Course not found",
            },
        },
    },
}

# Mô tả phản hồi lỗi 403 trong tài liệu OpenAPI/Swagger.
forbidden_response = {
    "description": "Forbidden",
    "content": {
        "application/json": {
            "example": {
                "message": "Forbidden",
            },
        },
    },
}


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: forbidden_response,
    },
)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """Tạo một khóa học mới."""

    return course_service.create_course(
        db=db,
        course_in=course_in,
        created_by=current_user_id,
        current_user_role=current_user_role,
    )


@router.get(
    "",
    response_model=list[CourseResponse],
    responses={
        status.HTTP_403_FORBIDDEN: forbidden_response,
    },
)
def list_courses(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    created_by: int | None = None,
) -> list[CourseResponse]:
    """Lấy danh sách khóa học chưa bị xóa mềm."""

    return course_service.list_courses(
        db=db,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
        skip=skip,
        limit=limit,
        created_by=created_by,
    )


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    responses={
        status.HTTP_403_FORBIDDEN: forbidden_response,
        status.HTTP_404_NOT_FOUND: not_found_response,
    },
)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """Lấy thông tin chi tiết của một khóa học."""

    course = course_service.get_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    responses={
        status.HTTP_403_FORBIDDEN: forbidden_response,
        status.HTTP_404_NOT_FOUND: not_found_response,
    },
)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """Cập nhật thông tin khóa học."""

    course = course_service.get_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course_service.update_course(
        db=db,
        db_obj=course,
        course_in=course_in,
        current_user_role=current_user_role,
    )


@router.delete(
    "/{course_id}",
    response_model=CourseResponse,
    responses={
        status.HTTP_403_FORBIDDEN: forbidden_response,
        status.HTTP_404_NOT_FOUND: not_found_response,
    },
)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """Xóa mềm một khóa học."""

    course = course_service.get_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course_service.soft_delete_course(
        db=db,
        db_obj=course,
        current_user_role=current_user_role,
    )