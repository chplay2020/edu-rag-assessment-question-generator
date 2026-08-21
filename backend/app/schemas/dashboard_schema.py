from pydantic import BaseModel
from typing import List

class ChartData(BaseModel):
    name: str
    value: int

class DashboardSummaryResponse(BaseModel):
    total_courses: int
    total_materials: int
    total_jobs: int
    total_generated_questions: int
    total_approved_questions: int
    total_rejected_questions: int
    validation_avg_score: float
    questions_by_difficulty: List[ChartData]
    questions_by_bloom: List[ChartData]
    questions_by_status: List[ChartData]
