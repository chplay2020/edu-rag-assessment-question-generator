from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema


class CourseBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    code: str | None = Field(default=None, max_length=100)


# Không nhận created_by từ client; backend sẽ lấy từ user đăng nhập.
class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    code: str | None = Field(default=None, max_length=100)


class CourseResponse(CourseBase):
    id: int
    created_by: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_deleted: bool = False
