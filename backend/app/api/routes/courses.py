from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.schemas.course_schema import CourseCreate, CourseResponse, CourseUpdate

router = APIRouter()

_courses: dict[int, CourseResponse] = {}
_next_course_id = 1
not_found_response = {
    "description": "Course not found",
    "content": {
        "application/json": {
            "example": {"message": "Course not found"},
        },
    },
}


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course_in: CourseCreate) -> CourseResponse:
    global _next_course_id

    course = CourseResponse(
        id=_next_course_id,
        created_by=1,
        created_at=datetime.now(),
        updated_at=None,
        is_deleted=False,
        **course_in.model_dump(),
    )
    _courses[_next_course_id] = course
    _next_course_id += 1
    return course


@router.get("", response_model=list[CourseResponse])
def list_courses(created_by: int | None = None) -> list[CourseResponse]:
    courses = [course for course in _courses.values() if not course.is_deleted]

    if created_by is not None:
        courses = [course for course in courses if course.created_by == created_by]

    return courses


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    responses={status.HTTP_404_NOT_FOUND: not_found_response},
)
def get_course(course_id: int) -> CourseResponse:
    course = _courses.get(course_id)
    if course is None or course.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    responses={status.HTTP_404_NOT_FOUND: not_found_response},
)
def update_course(course_id: int, course_in: CourseUpdate) -> CourseResponse:
    course = _courses.get(course_id)
    if course is None or course.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    update_data = course_in.model_dump(exclude_unset=True)
    updated_course = course.model_copy(
        update={
            **update_data,
            "updated_at": datetime.now(),
        }
    )
    _courses[course_id] = updated_course
    return updated_course


@router.delete(
    "/{course_id}",
    response_model=CourseResponse,
    responses={status.HTTP_404_NOT_FOUND: not_found_response},
)
def delete_course(course_id: int) -> CourseResponse:
    course = _courses.get(course_id)
    if course is None or course.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    deleted_course = course.model_copy(
        update={
            "is_deleted": True,
            "updated_at": datetime.now(),
        }
    )
    _courses[course_id] = deleted_course
    return deleted_course
