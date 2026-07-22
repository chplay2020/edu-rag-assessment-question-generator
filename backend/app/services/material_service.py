import os
import uuid
import shutil
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from app.models.material import Material
from app.services import course_service

# Cấu hình lưu trữ
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = [
    "application/pdf", 
    "text/plain", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]
ALLOWED_EXTENSIONS = ["pdf", "txt", "docx"]

def ensure_upload_dir_exists():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

def upload_material(
    db: Session, 
    course_id: int, 
    file: UploadFile, 
    current_user_id: int, 
    current_user_role: str
) -> Material:
    
    # 1. Kiểm tra course tồn tại và quyền (lecturer chỉ được sửa khóa mình tạo)
    course = course_service.get_course(
        db=db, 
        course_id=course_id, 
        current_user_id=current_user_id, 
        current_user_role=current_user_role
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại hoặc bạn không có quyền truy cập."
        )

    # 2. Validate loại file
    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else ""
    if file.content_type not in ALLOWED_MIME_TYPES and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ hỗ trợ upload định dạng PDF, TXT hoặc DOCX."
        )
            
    # Lấy kích thước file thực tế bằng cách di chuyển con trỏ đọc
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0) # Trả con trỏ về đầu để lưu
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kích thước file vượt quá giới hạn 10MB."
        )

    # 3. Tạo đường dẫn và lưu file
    ensure_upload_dir_exists()
    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Đảm bảo đường dẫn file dùng / 
    file_path = file_path.replace("\\", "/")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể ghi file vào ổ đĩa: {str(e)}"
        )

    # 4. Lưu thông tin vào Database
    db_obj = Material(
        title=file.filename or safe_filename,
        file_path=file_path,
        course_id=course_id,
        uploaded_by=current_user_id,
        status="processing"
    )
    db.add(db_obj)
    
    try:
        db.commit()
        db.refresh(db_obj)
    except Exception as e:
        db.rollback()
        # Dọn rác: Xóa file vừa lưu nếu insert DB thất bại
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lưu thông tin vào cơ sở dữ liệu."
        )
        
    return db_obj


def get_materials_by_course(
    db: Session, 
    course_id: int, 
    current_user_id: int, 
    current_user_role: str
) -> list[Material]:
    
    course = course_service.get_course(
        db=db, 
        course_id=course_id, 
        current_user_id=current_user_id, 
        current_user_role=current_user_role
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại hoặc bạn không có quyền truy cập."
        )
        
    return db.query(Material).filter(Material.course_id == course_id).order_by(Material.created_at.desc()).all()
