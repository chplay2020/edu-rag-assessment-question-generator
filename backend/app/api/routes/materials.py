from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from app.api.deps import get_db, get_current_user_id, get_current_user_role, get_current_active_lecturer
from app.schemas.material_schema import MaterialResponse, MaterialDetailResponse
from app.services import material_service

router = APIRouter()

@router.post("/upload", response_model=MaterialResponse, dependencies=[Depends(get_current_active_lecturer)])
def upload_material(
    course_id: int = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Upload tài liệu học tập (PDF, DOCX, TXT)"""
    return material_service.upload_material(
        db=db,
        course_id=course_id,
        file=file,
        current_user_id=current_user_id,
        current_user_role=current_user_role
    )

@router.get("/course/{course_id}", response_model=List[MaterialResponse], dependencies=[Depends(get_current_active_lecturer)])
def get_materials_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Lấy danh sách tài liệu của khóa học"""
    return material_service.get_materials_by_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role
    )

@router.get("/{material_id}", response_model=MaterialDetailResponse, dependencies=[Depends(get_current_active_lecturer)])
def get_material_detail(
    material_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> Any:
    """Lấy chi tiết tài liệu học tập"""
    return material_service.get_material_detail(
        db=db,
        material_id=material_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role
    )
