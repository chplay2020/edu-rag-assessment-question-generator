import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db, get_current_user
from app.models import Base
from app.models.course import Course
from app.models.material import Material, Job
from app.models.question import Question, QuestionValidationResult
from app.models.user import User

@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture()
def db_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

@pytest.fixture()
def db(db_session_factory):
    session = db_session_factory()
    try:
        yield session
    finally:
        session.close()

def _make_user(db, email: str, role: str = "lecturer") -> User:
    user = User(email=email, hashed_password="x", full_name=email, role=role, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def _make_course(db, user_id: int) -> Course:
    course = Course(title="C1", created_by=user_id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def _make_material(db, course_id: int, user_id: int) -> Material:
    material = Material(title="M1", course_id=course_id, uploaded_by=user_id, file_path="m1.pdf")
    db.add(material)
    db.commit()
    db.refresh(material)
    return material

def _make_question(db, course_id: int, material_id: int, status: str = "approved") -> Question:
    q = Question(course_id=course_id, material_id=material_id, content="Q1", status=status)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

def _make_validation(db, q_id: int, scores: dict):
    v = QuestionValidationResult(question_id=q_id, validator_type="llm_judge", score=scores)
    db.add(v)
    db.commit()

def test_get_dashboard_summary_lecturer(db):
    user = _make_user(db, "lecturer@test.com")
    c1 = _make_course(db, user.id)
    m1 = _make_material(db, c1.id, user.id)
    
    q1 = _make_question(db, c1.id, m1.id, "approved")
    q2 = _make_question(db, c1.id, m1.id, "rejected")
    
    _make_validation(db, q1.id, {"c": 8.0, "r": 9.0})
    _make_validation(db, q2.id, {"c": 7.0})

    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    client = TestClient(app)
    response = client.get("/api/v1/dashboard/summary")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_materials"] == 1
    assert data["total_generated_questions"] == 2
    assert data["total_approved_questions"] == 1
    assert data["total_rejected_questions"] == 1
    assert data["validation_avg_score"] == 8.0
    assert "questions_by_difficulty" in data
    assert "questions_by_bloom" in data
    assert "questions_by_status" in data

    app.dependency_overrides.clear()
