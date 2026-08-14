from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MaterialBase(BaseModel):
    title: str
    course_id: int

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: int
    uploaded_by: int
    file_url: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class MaterialDetailResponse(MaterialResponse):
    chunk_count: int
    extracted_text_preview: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    material_id: int
    task_type: str
    status: str
    config: Optional[dict] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaterialChunkResponse(BaseModel):
    chunk_id: int
    content: str
    chunk_index: Optional[int] = None
