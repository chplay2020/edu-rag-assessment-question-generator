from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import (
    get_current_user_id,
    get_current_user_role,
    get_current_active_lecturer,
    get_db,
)
from app.api.routes import questions as questions_router_module
from app.models import Base
from app.models.course import Course
from app.models.material import Material
from app.models.question import Question, Option, Review
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

def _seed(db, *, owner_email: str = "owner@example.com", other_email: str = "other@example.com") -> dict:
    owner = User(
        email=owner_email,
        hashed_password="x",
        full_name="Owner",
        role="lecturer",
        is_active=True,
    )
    other = User(
        email=other_email,
        hashed_password="x",
        full_name="Other",
        role="lecturer",
        is_active=True,
    )
    db.add_all([owner, other])
    db.commit()
    db.refresh(owner)
    db.refresh(other)

    course = Course(
        title="Course",
        code="C-001",
        description="",
        created_by=owner.id,
        is_deleted=False,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    material = Material(
        title="Lesson",
        file_path="/tmp/test.txt",
        status="processed",
        course_id=course.id,
        uploaded_by=owner.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return {
        "owner_id": owner.id,
        "other_id": other.id,
        "course_id": course.id,
        "material_id": material.id,
    }

def _seed_question(db, material_id: int, course_id: int, status: str = "draft") -> Question:
    q = Question(
        material_id=material_id,
        course_id=course_id,
        content="What is testing?",
        difficulty="Dễ",
        bloom_level="Nhận biết",
        question_type="multiple_choice",
        explanation="Testing is good",
        status=status,
    )
    q.options = [
        Option(content="Option A", is_correct=True),
        Option(content="Option B", is_correct=False),
    ]
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

def _make_app(db_session_factory, *, user_id: int, user_role: str) -> FastAPI:
    app = FastAPI()
    app.include_router(questions_router_module.router, prefix="/questions")

    session = db_session_factory()

    def override_db():
        try:
            yield session
        finally:
            pass

    def override_user_id():
        return user_id

    def override_user_role():
        return user_role

    def override_active_lecturer():
        from app.models.user import User as U
        return session.query(U).filter(U.id == user_id).first()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user_id] = override_user_id
    app.dependency_overrides[get_current_user_role] = override_user_role
    app.dependency_overrides[get_current_active_lecturer] = override_active_lecturer

    return app

# TC1: Permissions
def test_other_lecturer_cannot_access_question(db, db_session_factory):
    ids = _seed(db)
    q = _seed_question(db, ids["material_id"], ids["course_id"])
    app = _make_app(db_session_factory, user_id=ids["other_id"], user_role="lecturer")

    with TestClient(app) as client:
        # Edit question
        resp = client.put(f"/questions/{q.id}", json={"content": "New content"})
        assert resp.status_code in (404, 403)
        
        # Review question
        resp2 = client.post(f"/questions/{q.id}/review", json={"status": "approved", "feedback": ""})
        assert resp2.status_code in (404, 403)

# TC2: Filter
def test_filter_questions_by_status(db, db_session_factory):
    ids = _seed(db)
    _seed_question(db, ids["material_id"], ids["course_id"], status="draft")
    _seed_question(db, ids["material_id"], ids["course_id"], status="approved")
    
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        # All
        resp_all = client.get(f"/questions?course_id={ids['course_id']}")
        assert len(resp_all.json()) == 2

        # Approved
        resp_app = client.get(f"/questions?course_id={ids['course_id']}&status=approved")
        data = resp_app.json()
        assert len(data) == 1
        assert data[0]["status"] == "approved"

# TC3: Approve/Reject
def test_review_question(db, db_session_factory):
    ids = _seed(db)
    q = _seed_question(db, ids["material_id"], ids["course_id"], status="review_required")
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        # Approve
        resp = client.post(f"/questions/{q.id}/review", json={"status": "approved", "feedback": "Good job"})
        assert resp.status_code == 200
        
        db.expire_all()
        q_updated = db.query(Question).filter(Question.id == q.id).first()
        assert q_updated.status == "approved"
        
        # Check review log
        review = db.query(Review).filter(Review.question_id == q.id).first()
        assert review.status == "approved"
        assert review.feedback == "Good job"

# TC4: Edit & Downgrade
def test_edit_question_updates_options(db, db_session_factory):
    ids = _seed(db)
    q = _seed_question(db, ids["material_id"], ids["course_id"], status="draft")
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        update_data = {
            "content": "Edited content",
            "options": [
                {"content": "New A", "is_correct": False},
                {"content": "New B", "is_correct": True}
            ]
        }
        resp = client.put(f"/questions/{q.id}", json=update_data)
        assert resp.status_code == 200
        
        db.expire_all()
        q_updated = db.query(Question).filter(Question.id == q.id).first()
        assert q_updated.content == "Edited content"
        assert len(q_updated.options) == 2
        assert q_updated.options[0].content == "New A"
        assert q_updated.options[0].is_correct is False
        assert q_updated.options[1].content == "New B"
        assert q_updated.options[1].is_correct is True

def test_edit_approved_question_downgrades_to_draft(db, db_session_factory):
    ids = _seed(db)
    q = _seed_question(db, ids["material_id"], ids["course_id"], status="approved")
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        resp = client.put(f"/questions/{q.id}", json={"content": "Slight fix"})
        assert resp.status_code == 200
        
        db.expire_all()
        q_updated = db.query(Question).filter(Question.id == q.id).first()
        assert q_updated.status in ("draft", "review_required") # Status should be downgraded
