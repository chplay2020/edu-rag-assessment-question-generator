from typing import Annotated, Any, cast

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_lecturer,
    get_current_user_id,
    get_current_user_role,
    get_db,
)
from app.models.material import Job, Material
from app.schemas.material_schema import MaterialDetailResponse, MaterialResponse
from app.services import course_service, material_service
from app.workers.material_worker import process_material

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


@router.post(
    "/{material_id}/process",
    dependencies=[Depends(get_current_active_lecturer)],
)
def enqueue_material_processing(
    material_id: int,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
) -> dict[str, Any]:
    """Tạo job xử lý material và chạy nền."""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài liệu không tồn tại.",
        )

    course = course_service.get_course(
        db=db,
        course_id=cast(int, material.course_id),
        current_user_id=current_user_id,
        current_user_role=current_user_role,
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài liệu không tồn tại hoặc bạn không có quyền truy cập.",
        )

    material_status = cast(str, material.status)
    if material_status not in {"uploaded", "failed"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chỉ có thể xử lý tài liệu ở trạng thái uploaded hoặc failed.",
        )

    job = Job(
        material_id=material_id,
        task_type="process_material",
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_material, material_id)

    return {
        "material_id": material_id,
        "material_status": material_status,
        "job_id": cast(int, job.id),
        "job_status": cast(str, job.status),
        "task_type": cast(str, job.task_type),
    }


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
