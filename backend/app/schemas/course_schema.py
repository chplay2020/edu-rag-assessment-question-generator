from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CourseResponse(CourseBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
