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
from app.api.routes import jobs as jobs_router_module
from app.api.routes import materials as materials_router_module
from app.models import Base
from app.models.course import Course
from app.models.material import Chunk, Job, Material
from app.models.user import User
from app.core.storage import BACKEND_DIR, get_processed_dir
from app.workers import material_worker

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

def _seed(
    db,
    *,
    owner_email: str = "owner@example.com",
    other_email: str = "other@example.com",
    material_status: str = "uploaded",
    file_path: str = "/tmp/test.txt",
) -> dict:
    """Tạo owner, other_lecturer, course, material. Trả dict các id."""
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
    admin = User(
        email="admin@example.com",
        hashed_password="x",
        full_name="Admin",
        role="admin",
        is_active=True,
    )
    db.add_all([owner, other, admin])
    db.commit()
    db.refresh(owner)
    db.refresh(other)
    db.refresh(admin)

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
        file_path=file_path,
        status=material_status,
        course_id=course.id,
        uploaded_by=owner.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return {
        "owner_id": owner.id,
        "other_id": other.id,
        "admin_id": admin.id,
        "course_id": course.id,
        "material_id": material.id,
    }


def _make_app(db_session_factory, *, user_id: int, user_role: str) -> FastAPI:
    """Tạo FastAPI test app với dependency overrides."""
    from fastapi import FastAPI as FA
    app = FA()

    # Import routers
    from app.api.routes.materials import router as mat_router
    from app.api.routes.jobs import router as job_router

    app.include_router(mat_router, prefix="/materials")
    app.include_router(job_router, prefix="/jobs")

    # Override dependencies
    session = db_session_factory()

    def override_db():
        try:
            yield session
        finally:
            pass  # Giữ session mở để assert sau khi request

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


# Mock Qdrant + embedding cho worker tests
@pytest.fixture()
def qdrant_mock(monkeypatch):
    class FakeVS:
        def ensure_collections(self):
            pass
        def upsert_material_chunks(self, chunks, vectors):
            pass

    monkeypatch.setattr(
        material_worker,
        "embed_texts",
        lambda texts: [[0.1] * 3 for _ in texts],
    )
    monkeypatch.setattr(material_worker, "get_vector_store", lambda: FakeVS())


# 1. Material uploaded → 202, status chuyển processing, Job pending

def test_process_uploaded_material_returns_202(tmp_path, db, db_session_factory):
    file = tmp_path / "doc.txt"
    file.write_text("A" * 100)
    ids = _seed(db, material_status="uploaded", file_path=str(file))

    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    # Mock background task để không chạy thật
    added_tasks = []

    def mock_add_task(fn, *args, **kwargs):
        added_tasks.append((fn, args, kwargs))

    with TestClient(app, raise_server_exceptions=True) as client:
    
        from unittest.mock import patch
        with patch("fastapi.BackgroundTasks.add_task", side_effect=mock_add_task):
            resp = client.post(f"/materials/{ids['material_id']}/process")

    assert resp.status_code == 202, resp.text
    data = resp.json()
    assert data["material_id"] == ids["material_id"]
    assert data["material_status"] == "processing"
    assert data["job_status"] == "pending"
    assert data["task_type"] == "process_material"
    assert data["job_id"] > 0

    # Kiểm tra DB: Material → processing
    db.expire_all()
    mat = db.query(Material).filter(Material.id == ids["material_id"]).first()
    assert mat.status == "processing"

    # Kiểm tra DB: Job → pending
    job = db.query(Job).filter(Job.id == data["job_id"]).first()
    assert job is not None
    assert job.status == "pending"



# 2. Material failed → được phép thử lại
def test_process_failed_material_allowed(tmp_path, db, db_session_factory):
    file = tmp_path / "doc.txt"
    file.write_text("content")
    ids = _seed(db, material_status="failed", file_path=str(file))

    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        from unittest.mock import patch
        with patch("fastapi.BackgroundTasks.add_task"):
            resp = client.post(f"/materials/{ids['material_id']}/process")

    assert resp.status_code == 202, resp.text
    data = resp.json()
    assert data["material_status"] == "processing"
    assert data["job_status"] == "pending"


# 3. Material không tồn tại → 404
def test_process_nonexistent_material_returns_404(db, db_session_factory):
    ids = _seed(db)
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        resp = client.post("/materials/99999/process")

    assert resp.status_code == 404


# 4. Lecturer không phải owner → 404
def test_process_by_non_owner_lecturer_returns_404(db, db_session_factory):
    ids = _seed(db)
    app = _make_app(db_session_factory, user_id=ids["other_id"], user_role="lecturer")

    with TestClient(app) as client:
        resp = client.post(f"/materials/{ids['material_id']}/process")

    assert resp.status_code == 404



# 5. Material đang processing → 409
def test_process_already_processing_returns_409(db, db_session_factory):
    ids = _seed(db, material_status="processing")
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        resp = client.post(f"/materials/{ids['material_id']}/process")

    assert resp.status_code == 409



# 6. Material đã processed → 409
def test_process_already_processed_returns_409(db, db_session_factory):
    ids = _seed(db, material_status="processed")
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        resp = client.post(f"/materials/{ids['material_id']}/process")

    assert resp.status_code == 409


# 7. Đã có Job pending/running → 409, không tạo thêm Job
@pytest.mark.parametrize("existing_job_status", ["pending", "running"])
def test_process_with_existing_active_job_returns_409(
    existing_job_status, db, db_session_factory
):
    ids = _seed(db, material_status="uploaded")

    job = Job(
        material_id=ids["material_id"],
        task_type="process_material",
        status=existing_job_status,
    )
    db.add(job)
    db.commit()

    job_count_before = db.query(Job).filter(Job.material_id == ids["material_id"]).count()
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        resp = client.post(f"/materials/{ids['material_id']}/process")

    assert resp.status_code == 409
    db.expire_all()
    job_count_after = db.query(Job).filter(Job.material_id == ids["material_id"]).count()
    assert job_count_after == job_count_before, "Không được tạo thêm Job khi đã có active job"


def test_second_immediate_process_request_returns_409(
    tmp_path, db, db_session_factory
):

    file = tmp_path / "doc.txt"
    file.write_text("real content", encoding="utf-8")
    ids = _seed(db, material_status="uploaded", file_path=str(file))
    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")

    with TestClient(app) as client:
        from unittest.mock import patch

        with patch("fastapi.BackgroundTasks.add_task"):
            first = client.post(f"/materials/{ids['material_id']}/process")
            second = client.post(f"/materials/{ids['material_id']}/process")

    assert first.status_code == 202, first.text
    assert second.status_code == 409, second.text
    db.expire_all()
    jobs = (
        db.query(Job)
        .filter(
            Job.material_id == ids["material_id"],
            Job.task_type == "process_material",
            Job.status.in_(["pending", "running"]),
        )
        .all()
    )
    assert len(jobs) == 1


# 8. Worker thành công → Material processed, Job done, có finished_at

def test_worker_success_sets_processed_and_done(
    tmp_path, monkeypatch, db_session_factory, qdrant_mock
):
    file = tmp_path / "lesson.txt"
    file.write_text("A" * 900, encoding="utf-8")
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(material_worker, "SessionLocal", db_session_factory)

    db = db_session_factory()
    ids = _seed(db, material_status="uploaded", file_path=str(file))

    # Seed job pending (mô phỏng endpoint đã tạo)
    mat = db.query(Material).filter(Material.id == ids["material_id"]).first()
    mat.status = "processing"
    job = Job(
        material_id=ids["material_id"],
        task_type="process_material",
        status="pending",
    )
    db.add(job)
    db.add(mat)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()

    material_worker.process_material(ids["material_id"])

    db2 = db_session_factory()
    mat2 = db2.query(Material).filter(Material.id == ids["material_id"]).first()
    job2 = db2.query(Job).filter(Job.id == job_id).first()
    chunks = db2.query(Chunk).filter(Chunk.material_id == ids["material_id"]).all()
    db2.close()

    assert mat2.status == "processed"
    assert job2.status == "done"
    assert job2.finished_at is not None
    assert len(chunks) >= 1


# 9. Pipeline lỗi → Material failed, Job failed, có finished_at

def test_worker_failure_sets_failed_status(
    tmp_path, monkeypatch, db_session_factory
):
    missing_file = tmp_path / "does_not_exist.txt"
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(material_worker, "SessionLocal", db_session_factory)

    db = db_session_factory()
    ids = _seed(db, material_status="uploaded", file_path=str(missing_file))

    # Seed material processing + job pending
    mat = db.query(Material).filter(Material.id == ids["material_id"]).first()
    mat.status = "processing"
    job = Job(
        material_id=ids["material_id"],
        task_type="process_material",
        status="pending",
    )
    db.add(job)
    db.add(mat)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()

    with pytest.raises(Exception):
        material_worker.process_material(ids["material_id"])

    db2 = db_session_factory()
    mat2 = db2.query(Material).filter(Material.id == ids["material_id"]).first()
    job2 = db2.query(Job).filter(Job.id == job_id).first()
    db2.close()

    assert mat2.status == "failed"
    assert job2.status == "failed"
    assert job2.finished_at is not None


def test_duplicate_worker_does_not_take_over_running_job(
    tmp_path, monkeypatch, db_session_factory
):
    source = tmp_path / "lesson.txt"
    source.write_text("content", encoding="utf-8")
    monkeypatch.setattr(material_worker, "SessionLocal", db_session_factory)

    db = db_session_factory()
    ids = _seed(db, material_status="processing", file_path=str(source))
    job = Job(
        material_id=ids["material_id"],
        task_type="process_material",
        status="running",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()

    with pytest.raises(material_worker.MaterialProcessingError, match="already 'running'"):
        material_worker.process_material(ids["material_id"])

    check = db_session_factory()
    material = check.query(Material).filter(Material.id == ids["material_id"]).first()
    existing_job = check.query(Job).filter(Job.id == job_id).first()
    assert material.status == "processing"
    assert existing_job.status == "running"
    assert existing_job.finished_at is None
    check.close()


def test_default_processed_dir_is_backend_relative(monkeypatch, tmp_path):
    monkeypatch.delenv("PROCESSED_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    assert get_processed_dir() == (BACKEND_DIR / "storage/processed").resolve()


# 10. GET /jobs/{job_id}: owner/admin xem được, lecturer khác → 404
def _seed_with_job(db, owner_id: int, material_id: int, job_status: str = "pending") -> int:
    job = Job(
        material_id=material_id,
        task_type="process_material",
        status=job_status,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job.id


def test_get_job_status_by_owner(db, db_session_factory):
    ids = _seed(db)
    job_id = _seed_with_job(db, ids["owner_id"], ids["material_id"])

    app = _make_app(db_session_factory, user_id=ids["owner_id"], user_role="lecturer")
    with TestClient(app) as client:
        resp = client.get(f"/jobs/{job_id}")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == job_id
    assert data["task_type"] == "process_material"
    assert data["status"] == "pending"


def test_get_job_status_by_admin(db, db_session_factory):
    ids = _seed(db)
    job_id = _seed_with_job(db, ids["owner_id"], ids["material_id"])

    app = _make_app(db_session_factory, user_id=ids["admin_id"], user_role="admin")
    with TestClient(app) as client:
        resp = client.get(f"/jobs/{job_id}")

    assert resp.status_code == 200, resp.text


def test_get_job_status_by_other_lecturer_returns_404(db, db_session_factory):
    ids = _seed(db)
    job_id = _seed_with_job(db, ids["owner_id"], ids["material_id"])

    app = _make_app(db_session_factory, user_id=ids["other_id"], user_role="lecturer")
    with TestClient(app) as client:
        resp = client.get(f"/jobs/{job_id}")

    assert resp.status_code == 404
