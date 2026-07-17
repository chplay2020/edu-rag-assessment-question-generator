from typing import Generator
from app.core.database import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id() -> int:
    # TODO: Thay thế bằng xác thực người dùng động sử dụng giải mã JWT khi các task Auth/RBAC (T010/T011) hoàn thành.
    return 1

def get_current_user_role() -> str:
    # TODO: Thay thế bằng lấy quyền người dùng động khi các task Auth/RBAC (T010/T011) hoàn thành.
    return "admin"
