from pydantic import BaseModel
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: str | None = None
    code: str | None = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    code: str | None = None

class CourseResponse(CourseBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime | None = None
    is_deleted: bool

    class Config:
        from_attributes = True
