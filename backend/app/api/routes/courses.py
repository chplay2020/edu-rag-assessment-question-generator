from fastapi import APIRouter
from typing import List, Any
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseResponse
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
def get_courses() -> Any:
    """Lấy danh sách khóa học"""
    return [
        CourseResponse(
            id=1, code="CS101", name="Intro to CS", 
            description="Basic CS", is_active=True, 
            created_by=1, created_at=datetime.now(), updated_at=datetime.now()
        )
    ]

@router.post("/", response_model=CourseResponse)
def create_course(data: CourseCreate) -> Any:
    """Tạo khóa học mới"""
    return CourseResponse(
        id=2, code=data.code, name=data.name, 
        description=data.description, is_active=data.is_active, 
        created_by=1, created_at=datetime.now(), updated_at=datetime.now()
    )

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int) -> Any:
    """Lấy thông tin chi tiết khóa học"""
    return CourseResponse(
        id=course_id, code="CS101", name="Intro to CS", 
        description="Basic CS", is_active=True, 
        created_by=1, created_at=datetime.now(), updated_at=datetime.now()
    )

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, data: CourseUpdate) -> Any:
    """Cập nhật thông tin khóa học"""
    return CourseResponse(
        id=course_id, code=data.code or "CS101", name=data.name or "Intro to CS", 
        description=data.description, is_active=True, 
        created_by=1, created_at=datetime.now(), updated_at=datetime.now()
    )

@router.delete("/{course_id}")
def delete_course(course_id: int) -> Any:
    """Xóa khóa học"""
    return {"message": "Xóa thành công"}
