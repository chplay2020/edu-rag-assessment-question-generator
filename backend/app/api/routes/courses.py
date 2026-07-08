from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_id, get_current_user_role
from app.schemas.course_schema import CourseCreate, CourseResponse, CourseUpdate
from app.services import course_service

router = APIRouter()

# Schema phản hồi lỗi 404 mặc định cho tài liệu OpenAPI Swagger
not_found_response = {
    "description": "Course not found",
    "content": {
        "application/json": {
            "example": {"message": "Course not found"},
        },
    },
}


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """
    Tạo khóa học mới.
    
    - Client không cần gửi trường `created_by`. Hệ thống tự động gán theo user đăng nhập hiện tại.
    - Phân quyền: Chỉ 'admin' hoặc 'lecturer' mới được tạo. Các role khác trả về lỗi 403.
    """
    return course_service.create_course(
        db=db,
        course_in=course_in,
        created_by=current_user_id,
        current_user_role=current_user_role
    )


@router.get("", response_model=list[CourseResponse])
def list_courses(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    created_by: int | None = None,
) -> list[CourseResponse]:
    """
    Lấy danh sách các khóa học (không bao gồm khóa học đã bị xóa mềm).
    
    - **skip**: Số lượng bản ghi bỏ qua (mặc định 0, yêu cầu lớn hơn hoặc bằng 0).
    - **limit**: Giới hạn số lượng bản ghi trả về (mặc định 20, nằm trong khoảng 1 đến 100). Nếu vượt quá 100 sẽ trả về mã lỗi 422.
    - **created_by**: Chỉ áp dụng khi role là 'admin' để lọc khóa học theo ID người tạo.
    - Phân quyền:
        - `admin` xem được toàn bộ khóa học.
        - `lecturer` chỉ xem được các khóa học do chính mình tạo (hệ thống tự động lọc theo ID của lecturer).
    """
    return course_service.list_courses(
        db=db,
        current_user_id=current_user_id,
        current_user_role=current_user_role,
        skip=skip,
        limit=limit,
        created_by=created_by
    )


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    responses={status.HTTP_404_NOT_FOUND: not_found_response},
)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """
    Lấy thông tin chi tiết một khóa học.
    
    - Trả về lỗi 404 nếu khóa học không tồn tại, đã bị xóa mềm hoặc nếu user là `lecturer` và truy cập khóa học của người khác.
    """
    course = course_service.get_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role
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
    responses={status.HTTP_404_NOT_FOUND: not_found_response},
)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """
    Cập nhật thông tin khóa học.
    
    - Kiểm tra sự tồn tại và quyền sở hữu trước khi cập nhật.
    - Nếu thành công, trường `updated_at` sẽ ghi nhận thời gian UTC hiện tại.
    """
    course = course_service.get_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role
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
        current_user_role=current_user_role
    )


@router.delete(
    "/{course_id}",
    response_model=CourseResponse,
    responses={status.HTTP_404_NOT_FOUND: not_found_response},
)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
) -> CourseResponse:
    """
    Xóa mềm một khóa học.
    
    - Đặt trạng thái `is_deleted` thành `True` và cập nhật trường `updated_at` thành giờ UTC hiện tại.
    - Không thực hiện xóa cứng (vẫn lưu bản ghi trong database).
    """
    course = course_service.get_course(
        db=db,
        course_id=course_id,
        current_user_id=current_user_id,
        current_user_role=current_user_role
    )
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course_service.soft_delete_course(
        db=db,
        db_obj=course,
        current_user_role=current_user_role
    )
