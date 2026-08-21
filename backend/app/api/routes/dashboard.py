from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.dashboard_schema import DashboardSummaryResponse
from app.schemas.auth_schema import UserResponse
from app.services import dashboard_service

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return dashboard_service.get_dashboard_summary(db, current_user.id, current_user.role)
