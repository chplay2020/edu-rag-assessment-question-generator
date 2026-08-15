"""Tests cho recover_orphaned_processing_materials.

Các case:
  1. processing + không có Job active → reset về uploaded
  2. processing + Job pending           → giữ processing
  3. processing + Job running           → giữ processing
  4. processed / failed / uploaded      → không đổi
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.course import Course
from app.models.material import Job, Material
from app.models.user import User
from app.services.material_service import recover_orphaned_processing_materials


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
def db(db_engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_material(db, *, status: str = "processing") -> Material:
    """Tạo user, course, material với status cho trước. Trả về Material."""
    uid = uuid.uuid4().hex[:8]
    user = User(
        email=f"u_{uid}@example.com",
        hashed_password="x",
        full_name="Test",
        role="lecturer",
        is_active=True,
    )
    db.add(user)
    db.flush()

    course = Course(
        title="Course",
        code=f"C-{uid}",
        description="",
        created_by=user.id,
        is_deleted=False,
    )
    db.add(course)
    db.flush()

    material = Material(
        title="Doc",
        file_path="/tmp/doc.txt",
        status=status,
        course_id=course.id,
        uploaded_by=user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def _add_job(db, material_id: int, job_status: str) -> Job:
    job = Job(
        material_id=material_id,
        task_type="process_material",
        status=job_status,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

# Case 1: processing, không có Job active → reset về uploaded
def test_orphaned_processing_resets_to_uploaded(db):
    mat = _seed_material(db, status="processing")
    # Không có Job nào

    affected = recover_orphaned_processing_materials(db, material_ids=[mat.id])

    db.expire_all()
    mat_after = db.query(Material).filter(Material.id == mat.id).first()
    assert mat_after.status == "uploaded"
    assert mat.id in affected


# Case 2: processing + Job pending → giữ processing
def test_processing_with_pending_job_is_untouched(db):
    mat = _seed_material(db, status="processing")
    _add_job(db, mat.id, "pending")

    affected = recover_orphaned_processing_materials(db, material_ids=[mat.id])

    db.expire_all()
    mat_after = db.query(Material).filter(Material.id == mat.id).first()
    assert mat_after.status == "processing"
    assert mat.id not in affected


# Case 3: processing + Job running → giữ processing
def test_processing_with_running_job_is_untouched(db):
    mat = _seed_material(db, status="processing")
    _add_job(db, mat.id, "running")

    affected = recover_orphaned_processing_materials(db, material_ids=[mat.id])

    db.expire_all()
    mat_after = db.query(Material).filter(Material.id == mat.id).first()
    assert mat_after.status == "processing"
    assert mat.id not in affected


# Case 4a: status = uploaded → không đổi
def test_uploaded_material_untouched(db):
    mat = _seed_material(db, status="uploaded")

    affected = recover_orphaned_processing_materials(db, material_ids=[mat.id])

    db.expire_all()
    mat_after = db.query(Material).filter(Material.id == mat.id).first()
    assert mat_after.status == "uploaded"
    assert mat.id not in affected


# Case 4b: status = processed → không đổi
def test_processed_material_untouched(db):
    mat = _seed_material(db, status="processed")

    affected = recover_orphaned_processing_materials(db, material_ids=[mat.id])

    db.expire_all()
    mat_after = db.query(Material).filter(Material.id == mat.id).first()
    assert mat_after.status == "processed"
    assert mat.id not in affected


# Case 4c: status = failed → không đổi
def test_failed_material_untouched(db):
    mat = _seed_material(db, status="failed")

    affected = recover_orphaned_processing_materials(db, material_ids=[mat.id])

    db.expire_all()
    mat_after = db.query(Material).filter(Material.id == mat.id).first()
    assert mat_after.status == "failed"
    assert mat.id not in affected


# Case 5: nhiều material, chỉ reset đúng những cái bị kẹt
def test_bulk_recover_only_resets_orphaned(db):
    orphaned = _seed_material(db, status="processing")  # không có job
    with_pending = _seed_material(db, status="processing")
    _add_job(db, with_pending.id, "pending")
    ok_processed = _seed_material(db, status="processed")

    all_ids = [orphaned.id, with_pending.id, ok_processed.id]
    affected = recover_orphaned_processing_materials(db, material_ids=all_ids)

    db.expire_all()
    assert db.query(Material).filter(Material.id == orphaned.id).first().status == "uploaded"
    assert db.query(Material).filter(Material.id == with_pending.id).first().status == "processing"
    assert db.query(Material).filter(Material.id == ok_processed.id).first().status == "processed"
    assert affected == {orphaned.id}
