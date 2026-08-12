from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_lecturer,
    get_current_user_id,
    get_current_user_role,
    get_db,
)
from app.schemas.material_schema import MaterialDetailResponse, MaterialResponse
from app.services import material_service

router = APIRouter()


@router.post(
    "/upload",
    response_model=MaterialResponse,
    dependencies=[Depends(get_current_active_lecturer)],
)
def upload_material(
    course_id: Annotated[int, Form(...)],
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
) -> Any:
    """Upload tài liệu học tập (PDF, TXT)."""
    return material_service.upload_material(
        db=db,
        course_id=course_id,
        file=file,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )


@router.get(
    "/course/{course_id}",
    response_model=list[MaterialResponse],
    dependencies=[Depends(get_current_active_lecturer)],
)
def get_materials_by_course(
    course_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
) -> Any:
    """Lấy danh sách tài liệu của khóa học."""
    return material_service.get_materials_by_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )


@router.get(
    "/{material_id}",
    response_model=MaterialDetailResponse,
    dependencies=[Depends(get_current_active_lecturer)],
)
def get_material_detail(
    material_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
) -> Any:
    """Lấy chi tiết tài liệu học tập."""
    return material_service.get_material_detail(
        db=db,
        material_id=material_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
