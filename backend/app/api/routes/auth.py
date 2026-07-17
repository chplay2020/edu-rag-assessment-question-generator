from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from app.schemas.auth_schema import UserLogin, UserCreate, UserResponse, Token
from datetime import datetime

router = APIRouter()

@router.post("/login", response_model=Token)
def login(data: UserLogin) -> Any:
    """Đăng nhập và nhận JWT token"""
    return {"access_token": "mock_token_123", "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
def register(data: UserCreate) -> Any:
    """Đăng ký tài khoản mới"""
    return UserResponse(id=1, username=data.username, full_name=data.full_name, role="user")

@router.get("/me", response_model=UserResponse)
def get_current_user() -> Any:
    """Lấy thông tin tài khoản hiện tại"""
    return UserResponse(id=1, username="testuser", full_name="Test User", role="user")
