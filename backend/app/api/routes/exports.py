from fastapi import APIRouter
from typing import Any
from app.schemas.export_schema import ExportResponse
from datetime import datetime

router = APIRouter()

@router.post("/course/{course_id}", response_model=ExportResponse)
def export_questions(course_id: int, format: str = "excel") -> Any:
    """Xuất câu hỏi ra file Excel/Aiken"""
    return ExportResponse(
        id=1, course_id=course_id, export_format=format,
        file_url=f"/exports/course_{course_id}.{format}",
        created_at=datetime.now()
    )
