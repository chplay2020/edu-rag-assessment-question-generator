import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import materials
from app.models import Base
from app.models.course import Course
from app.models.material import Chunk, Material
from app.models.user import User
from app.workers import material_worker


@pytest.fixture()
def db_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def _seed_material(db_session_factory, file_path: str, status: str = "uploaded") -> int:
    db = db_session_factory()
    user = User(
        email="lecturer@example.com",
        hashed_password="hash",
        full_name="Lecturer",
        role="lecturer",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    course = Course(
        title="Course",
        code="COURSE-1",
        description="",
        created_by=user.id,
        is_deleted=False,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    material = Material(
        title="Lesson",
        file_path=file_path,
        status=status,
        course_id=course.id,
        uploaded_by=user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    material_id = material.id
    db.close()
    return material_id


def test_worker_success_sets_material_processed_and_inserts_chunks(
    tmp_path, monkeypatch, db_session_factory
):
    source = tmp_path / "lesson.txt"
    source.write_text("A" * 900, encoding="utf-8")
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(material_worker, "SessionLocal", db_session_factory)
    material_id = _seed_material(db_session_factory, str(source))

    material_worker.process_material(material_id)

    db = db_session_factory()
    material = db.query(Material).filter(Material.id == material_id).first()
    chunks = db.query(Chunk).filter(Chunk.material_id == material_id).all()
    db.close()

    assert material is not None
    assert material.status == "processed"
    assert len(chunks) >= 1
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_worker_failure_sets_material_failed(tmp_path, monkeypatch, db_session_factory):
    missing_file = tmp_path / "missing.txt"
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(material_worker, "SessionLocal", db_session_factory)
    material_id = _seed_material(db_session_factory, str(missing_file))

    with pytest.raises(Exception):
        material_worker.process_material(material_id)

    db = db_session_factory()
    material = db.query(Material).filter(Material.id == material_id).first()
    db.close()

    assert material is not None
    assert material.status == "failed"


def test_endpoint_process_material_exists():
    matching_routes = [
        route
        for route in materials.router.routes
        if getattr(route, "path", None) == "/{material_id}/process"
        and "POST" in getattr(route, "methods", set())
    ]

    assert matching_routes
