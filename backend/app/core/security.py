from datetime import datetime, timedelta, timezone
from typing import Any, Optional, cast
import jwt  # type: ignore
from passlib.context import CryptContext  # type: ignore
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context_any = cast(Any, pwd_context)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context_any.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return cast(str, pwd_context_any.hash(password))


def create_access_token(
    subject: Any, expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode: dict[str, Any] = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)  # type: ignore[return-value]
    return encoded_jwt
