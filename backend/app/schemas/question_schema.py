from pydantic import BaseModel, Field
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
    difficulty: str = "medium"
    bloom_level: Optional[str] = None
    question_type: str = "multiple_choice"
    explanation: Optional[str] = None
    source_chunk_ids: Optional[List[int]] = None

class QuestionCreate(QuestionBase):
    material_id: int
    course_id: int
    status: str = "draft"
    options: List[OptionBase]

class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    difficulty: Optional[str] = None
    bloom_level: Optional[str] = None
    question_type: Optional[str] = None
    explanation: Optional[str] = None
    source_chunk_ids: Optional[List[int]] = None
    status: Optional[str] = None

class QuestionResponse(QuestionBase):
    id: int
    material_id: int
    course_id: int
    job_id: Optional[int] = None
    status: str
    created_at: datetime
    options: List[OptionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    status: str
    feedback: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    question_id: int
    reviewed_by: int
    status: str
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
