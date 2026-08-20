from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class ExportRequest(BaseModel):
    question_ids: List[int] = Field(..., min_length=1, max_length=200)

class ExportItem(BaseModel):
    id: int
    course_id: Optional[int]
    question_ids: List[int]
    format: str
    created_at: datetime
    file_name: str = Field(validation_alias="file_path")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ExportListResponse(BaseModel):
    items: List[ExportItem]
    total: int
    skip: int
    limit: int
