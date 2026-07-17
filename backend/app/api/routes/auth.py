from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.auth_schema import UserCreate, UserResponse, Token
from app.services import auth_service
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """Đăng nhập và nhận JWT token"""
    user = auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai email hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """Đăng ký tài khoản mới"""
    user = auth_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký",
        )
    user = auth_service.create_user(db, user_in=user_in)
    return user

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)) -> Any:
    """Lấy thông tin tài khoản hiện tại"""
    return current_user

@router.post("/logout")
def logout() -> Any:
    """Đăng xuất (client tự xóa token)"""
    return {"message": "Đăng xuất thành công"}
