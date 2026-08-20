from pydantic import BaseModel, Field
from typing import List

class ExportRequest(BaseModel):
    question_ids: List[int] = Field(..., min_length=1, max_length=200)
