from fastapi import APIRouter
from typing import Any
from app.schemas.material_schema import JobResponse
from datetime import datetime

router = APIRouter()

@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(job_id: int) -> Any:
    """Kiểm tra tiến độ trích xuất AI"""
    return JobResponse(
        id=job_id, material_id=1, job_type="extract_questions",
        status="in_progress", progress=45,
        created_at=datetime.now(), updated_at=datetime.now()
    )
