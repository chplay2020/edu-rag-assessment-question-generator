from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.api.deps import get_current_active_lecturer
from typing import List, Any
from app.schemas.material_schema import MaterialResponse
from datetime import datetime

router = APIRouter()

@router.post("/upload", response_model=MaterialResponse, dependencies=[Depends(get_current_active_lecturer)])
def upload_material(course_id: int = Form(...), file: UploadFile = File(...)) -> Any:
    """Upload tài liệu học tập (PDF, DOCX)"""
    return MaterialResponse(
        id=1, 
        title=file.filename or "uploaded_file", 
        course_id=course_id, 
        uploaded_by=1,
        status="processing", 
        created_at=datetime.now()
    )

@router.get("/course/{course_id}", response_model=List[MaterialResponse])
def get_materials_by_course(course_id: int) -> Any:
    """Lấy danh sách tài liệu của khóa học"""
    return [
        MaterialResponse(
            id=1, 
            title="Syllabus.pdf", 
            course_id=course_id, 
            uploaded_by=1,
            status="done", 
            file_url="/storage/Syllabus.pdf",
            created_at=datetime.now()
        )
    ]
