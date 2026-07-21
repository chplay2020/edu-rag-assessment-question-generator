from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.course import Course
from app.schemas.course_schema import CourseCreate, CourseUpdate

def create_course(db: Session, course_in: CourseCreate, created_by: int, current_user_role: str) -> Course:
   
    # Tạo một khóa học mới.
    
    # Kiểm tra phân quyền vai trò người dùng
    if current_user_role not in ["admin", "lecturer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
        
    # Tạo đối tượng Course mới
    db_obj = Course(
        title=course_in.title,
        description=course_in.description,
        code=course_in.code,
        created_by=created_by
    )
    db.add(db_obj)
    try:
        db.commit()
        db.refresh(db_obj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mã môn học đã tồn tại. Vui lòng chọn mã khác."
        )
    return db_obj

def list_courses(
    db: Session,
    current_user_id: int,
    current_user_role: str,
    skip: int = 0,
    limit: int = 20,
    created_by: int | None = None
) -> list[Course]:
    
    # Lấy danh sách các khóa học chưa bị xóa mềm.
    
    # Kiểm tra phân quyền vai trò người dùng
    if current_user_role not in ["admin", "lecturer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    
    # Chỉ truy vấn các khóa học chưa bị xóa mềm (is_deleted là False)
    query = db.query(Course).filter(Course.is_deleted.is_(False))
    
    # Áp dụng bộ lọc tùy theo vai trò
    if current_user_role == "admin":
        if created_by is not None:
            query = query.filter(Course.created_by == created_by)
    elif current_user_role == "lecturer":
        query = query.filter(Course.created_by == current_user_id)
        
    return query.offset(skip).limit(limit).all()

def get_course(
    db: Session,
    course_id: int,
    current_user_id: int,
    current_user_role: str
) -> Course | None:

    # Lấy thông tin chi tiết của một khóa học theo ID.
    
    # Kiểm tra phân quyền vai trò người dùng
    if current_user_role not in ["admin", "lecturer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
        
    # Tìm khóa học chưa bị xóa mềm
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted.is_(False)).first()
    if not course:
        return None
        
    # Kiểm tra quyền sở hữu đối với lecturer
    if current_user_role == "lecturer" and course.created_by != current_user_id:
        return None
        
    return course

def update_course(
    db: Session,
    db_obj: Course,
    course_in: CourseUpdate,
    current_user_role: str
) -> Course:

    # Cập nhật thông tin của khóa học.
    # Kiểm tra phân quyền vai trò người dùng
    if current_user_role not in ["admin", "lecturer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
        
    # Cập nhật các trường dữ liệu do client gửi lên
    update_data = course_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
        
    # Ghi nhận thời gian cập nhật theo giờ UTC
    db_obj.updated_at = datetime.now(timezone.utc)
    
    db.add(db_obj)
    try:
        db.commit()
        db.refresh(db_obj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mã môn học đã tồn tại. Vui lòng chọn mã khác."
        )
    return db_obj

def soft_delete_course(
    db: Session,
    db_obj: Course,
    current_user_role: str
) -> Course:

    # Xóa mềm một khóa học (chuyển trạng thái is_deleted sang True).
    # Kiểm tra phân quyền vai trò người dùng
    if current_user_role not in ["admin", "lecturer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
        
    # Đánh dấu xóa mềm và lưu thời gian cập nhật theo giờ UTC
    db_obj.is_deleted = True
    db_obj.updated_at = datetime.now(timezone.utc)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
