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
from app.schemas.material_schema import (
    MaterialDetailResponse,
    MaterialProcessResponse,
    MaterialResponse,
)
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
    response_model=MaterialProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_current_active_lecturer)],
)
def enqueue_material_processing(
    material_id: int,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    current_user_role: Annotated[str, Depends(get_current_user_role)],
) -> MaterialProcessResponse:
    """Tạo job xử lý material và chạy nền.

    - Chỉ owner của course hoặc Admin được xử lý.
    - Chỉ cho phép bắt đầu khi trạng thái Material là ``uploaded`` hoặc ``failed``.
    - Trả ``409 Conflict`` nếu Material đang ``processing`` / ``processed``
      hoặc đã có Job ``pending``/``running`` cho cùng material.
    - Tạo Job và cập nhật Material sang ``processing`` trong cùng một transaction
      trước khi đưa task vào BackgroundTasks.
    """
    try:
        # PostgreSQL serializes concurrent process requests for one Material.
        # The lock is held until Job creation and the status update are committed.
        material = (
            db.query(Material)
            .filter(Material.id == material_id)
            .with_for_update()
            .first()
        )
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
        if material_status in {"processing", "processed"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Tài liệu đang ở trạng thái '{material_status}', "
                    "không thể khởi tạo lại."
                ),
            )
        if material_status not in {"uploaded", "failed"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chỉ có thể xử lý tài liệu ở trạng thái uploaded hoặc failed.",
            )

        existing_job = (
            db.query(Job)
            .filter(
                Job.material_id == material_id,
                Job.task_type == "process_material",
                Job.status.in_(["pending", "running"]),
            )
            .first()
        )
        if existing_job:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Đã có job '{existing_job.status}' đang chờ xử lý "
                    f"(job_id={existing_job.id}). Không tạo job trùng."
                ),
            )

        job = Job(
            material_id=material_id,
            task_type="process_material",
            status="pending",
        )
        material.status = "processing"
        db.add_all([job, material])
        db.flush()

        response = MaterialProcessResponse(
            material_id=material_id,
            material_status="processing",
            job_id=cast(int, job.id),
            job_status="pending",
            task_type="process_material",
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    # The background task is registered only after the transaction is durable.
    background_tasks.add_task(process_material, material_id)
    return response


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
