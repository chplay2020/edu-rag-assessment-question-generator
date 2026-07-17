from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OptionBase(BaseModel):
    content: str
    is_correct: bool

class OptionResponse(OptionBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    content: str
    difficulty_level: int
    blooms_taxonomy: Optional[str] = None

class QuestionCreate(QuestionBase):
    material_id: Optional[int] = None
    course_id: int
    options: List[OptionBase]

class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    difficulty_level: Optional[int] = None
    blooms_taxonomy: Optional[str] = None
    status: Optional[str] = None

class QuestionResponse(QuestionBase):
    id: int
    material_id: Optional[int] = None
    course_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    options: List[OptionResponse]

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    action: str
    comments: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    question_id: int
    reviewer_id: int
    action: str
    comments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
