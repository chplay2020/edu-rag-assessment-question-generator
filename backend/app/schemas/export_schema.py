from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExportResponse(BaseModel):
    id: int
    course_id: int
    export_format: str
    file_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
