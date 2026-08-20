from __future__ import annotations
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.api.deps import (
    get_db,
    get_current_user_id,
    get_current_user_role,
    get_current_active_lecturer,
)
from app.models import Base
from app.models.course import Course
from app.models.material import Job, Material
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

def _seed(db, *, material_status: str = "processed") -> dict:
    user = User(
        email="lecturer@test.com",
        hashed_password="x",
        full_name="Lecturer",
        role="lecturer",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    course = Course(
        title="Course",
        code="C-001",
        description="",
        created_by=user.id,
        is_deleted=False,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    material = Material(
        title="Tài liệu mẫu",
        file_path="/tmp/sample.txt",
        status=material_status,
        course_id=course.id,
        uploaded_by=user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return {
        "user_id": user.id,
        "course_id": course.id,
        "material_id": material.id,
    }


def _make_app(db_session_factory, *, user_id: int, user_role: str = "lecturer") -> FastAPI:
    app = FastAPI()

    from app.api.routes.jobs import router as jobs_router
    app.include_router(jobs_router, prefix="/jobs")

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
        return session.query(User).filter(User.id == user_id).first()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user_id] = override_user_id
    app.dependency_overrides[get_current_user_role] = override_user_role
    app.dependency_overrides[get_current_active_lecturer] = override_active_lecturer

    return app

def test_generate_questions_json_body_creates_job(db, db_session_factory):
    """POST /jobs/material/{id}/generate-questions nhận JSON body và tạo job."""
    ids = _seed(db, material_status="processed")
    app = _make_app(db_session_factory, user_id=ids["user_id"])

    payload = {
        "number_of_questions": 5,
        "difficulty": "medium",
        "language": "vi",
        "top_k": 5,
    }

    with TestClient(app) as client:
        with patch("fastapi.BackgroundTasks.add_task"):
            resp = client.post(
                f"/jobs/material/{ids['material_id']}/generate-questions",
                json=payload,
            )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    # Response phải có đúng field names mà frontend kỳ vọng: id, status (không phải job_id, job_status)
    assert "id" in data, f"Response thiếu 'id': {data}"
    assert "status" in data, f"Response thiếu 'status': {data}"
    assert data["task_type"] == "generate_questions"
    assert data["status"] == "pending"
    assert data["material_id"] == ids["material_id"]
    assert data["id"] > 0

    # Quan trọng: config phải được lưu vào DB
    db.expire_all()
    job = db.query(Job).filter(Job.id == data["id"]).first()
    assert job is not None
    assert job.config is not None
    assert job.config["number_of_questions"] == 5
    assert job.config["difficulty"] == "medium"
    assert job.config["language"] == "vi"

def test_generate_questions_with_optional_fields(db, db_session_factory):
    """bloom_level và query (optional) được lưu đúng vào config."""
    ids = _seed(db, material_status="processed")
    app = _make_app(db_session_factory, user_id=ids["user_id"])

    payload = {
        "number_of_questions": 3,
        "difficulty": "hard",
        "language": "vi",
        "top_k": 5,
        "bloom_level": "analyze",
        "query": "Chỉ tập trung vào chương 2",
    }

    with TestClient(app) as client:
        with patch("fastapi.BackgroundTasks.add_task"):
            resp = client.post(
                f"/jobs/material/{ids['material_id']}/generate-questions",
                json=payload,
            )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] > 0, f"'id' phải là số nguyên dương: {data}"
    db.expire_all()
    job = db.query(Job).filter(Job.id == data["id"]).first()
    assert job.config["bloom_level"] == "analyze"
    assert job.config["query"] == "Chỉ tập trung vào chương 2"
    assert job.config["difficulty"] == "hard"


def test_generate_questions_returns_409_when_material_not_processed(db, db_session_factory):
    """Phải trả 409 (không phải 500) khi material chưa processed."""
    ids = _seed(db, material_status="uploaded")
    app = _make_app(db_session_factory, user_id=ids["user_id"])

    with TestClient(app) as client:
        resp = client.post(
            f"/jobs/material/{ids['material_id']}/generate-questions",
            json={"number_of_questions": 5, "difficulty": "medium", "language": "vi", "top_k": 5},
        )

    assert resp.status_code == 409, resp.text
    assert "processed" in resp.json()["detail"]

    # Không có job nào được tạo
    db.expire_all()
    assert db.query(Job).count() == 0

def test_generate_questions_returns_404_for_nonexistent_material(db, db_session_factory):
    """Phải trả 404 khi material_id không tồn tại."""
    ids = _seed(db)
    app = _make_app(db_session_factory, user_id=ids["user_id"])

    with TestClient(app) as client:
        resp = client.post(
            "/jobs/material/99999/generate-questions",
            json={"number_of_questions": 5, "difficulty": "medium", "language": "vi", "top_k": 5},
        )

    assert resp.status_code == 404

def test_generate_questions_validates_number_of_questions(db, db_session_factory):
    """number_of_questions = 0 phải trả 422 Unprocessable Entity."""
    ids = _seed(db)
    app = _make_app(db_session_factory, user_id=ids["user_id"])

    with TestClient(app) as client:
        resp = client.post(
            f"/jobs/material/{ids['material_id']}/generate-questions",
            json={"number_of_questions": 0, "difficulty": "medium", "language": "vi", "top_k": 5},
        )

    assert resp.status_code == 422

def test_generate_questions_requires_auth():
    """Endpoint phải từ chối khi không có auth."""
    app = FastAPI()
    from app.api.routes.jobs import router as jobs_router
    app.include_router(jobs_router, prefix="/jobs")

    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.post(
            "/jobs/material/1/generate-questions",
            json={"number_of_questions": 5, "difficulty": "medium", "language": "vi", "top_k": 5},
        )

    assert resp.status_code in (401, 403, 422)

def test_generate_questions_endpoint_accepts_json_body_not_query_params(db, db_session_factory):
    """Gửi params qua query string thay vì body → vẫn dùng giá trị default từ body schema."""
    ids = _seed(db, material_status="processed")
    app = _make_app(db_session_factory, user_id=ids["user_id"])

    with TestClient(app) as client:
        with patch("fastapi.BackgroundTasks.add_task"):
            resp = client.post(
                f"/jobs/material/{ids['material_id']}/generate-questions",
                json={}, 
            )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    # Kiểm tra field names đúng contract frontend
    assert "id" in data and data["id"] > 0, f"'id' phải là số nguyên dương: {data}"
    assert "status" in data, f"'status' phải tồn tại: {data}"
    assert "job_id" not in data, f"'job_id' không được xuất hiện (frontend dùng 'id'): {data}"
    assert "job_status" not in data, f"'job_status' không được xuất hiện (frontend dùng 'status'): {data}"
    db.expire_all()
    job = db.query(Job).filter(Job.id == data["id"]).first()

    assert job.config["number_of_questions"] == 5
