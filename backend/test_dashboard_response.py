import sys
from app.core.database import SessionLocal
from app.models.user import User
from app.services.dashboard_service import get_dashboard_summary

def test_db():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        print("No user")
        return
    summary = get_dashboard_summary(db, user.id, user.role)
    print(summary.model_dump())

if __name__ == "__main__":
    test_db()
