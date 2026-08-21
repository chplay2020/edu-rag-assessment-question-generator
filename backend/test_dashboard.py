import sys
from app.core.database import SessionLocal
from app.models.material import Material, Job, Chunk; from app.models.course import Course
from app.models.user import User
from app.models.question import Question, QuestionValidationResult
from app.services.dashboard_service import get_dashboard_summary

def test_db():
    db = SessionLocal()
    user = db.query(User).first()
    
    summary = get_dashboard_summary(db, user.id, user.role)
    print(summary)

    db.close()
    print("SUCCESS")

if __name__ == "__main__":
    test_db()
