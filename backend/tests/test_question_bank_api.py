from __future__ import annotations
# pyrefly: ignore [missing-import]
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db, get_current_active_lecturer
from app.models import Base
from app.models.course import Course
from app.models.material import Material
from app.models.question import Option, Question
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

def _seed_base(db) -> dict:
    """Tạo user, course, material cơ bản. Trả dict có user_id, course_id, material_id."""
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
        title="Toán học",
        code="MATH-001",
        description="",
        created_by=user.id,
        is_deleted=False,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    material = Material(
        title="Chương 1",
        file_path="/tmp/ch1.txt",
        status="processed",
        course_id=course.id,
        uploaded_by=user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return {"user_id": user.id, "course_id": course.id, "material_id": material.id}


def _make_question(
    db,
    *,
    material_id: int,
    course_id: int,
    status: str = "approved",
    difficulty: str = "medium",
    bloom_level: str = "remember",
    question_type: str = "multiple_choice",
    content: str = "Câu hỏi mẫu?",
) -> Question:
    q = Question(
        material_id=material_id,
        course_id=course_id,
        content=content,
        difficulty=difficulty,
        bloom_level=bloom_level,
        question_type=question_type,
        status=status,
    )
    db.add(q)
    db.flush()
    db.add(Option(question_id=q.id, content="A", is_correct=True))
    db.add(Option(question_id=q.id, content="B", is_correct=False))
    db.commit()
    db.refresh(q)
    return q


def _qkw(ids: dict) -> dict:
    """Lấy chỉ material_id và course_id từ ids dict để truyền vào _make_question."""
    return {"material_id": ids["material_id"], "course_id": ids["course_id"]}


def _make_app(db_session_factory, *, user_id: int, user_role: str = "lecturer") -> FastAPI:
    """Tạo FastAPI test app với dependency overrides cho question_bank router."""
    app = FastAPI()

    from app.api.routes.question_bank import router as bank_router
    app.include_router(bank_router, prefix="/questions")

    session = db_session_factory()

    def override_db():
        try:
            yield session
        finally:
            pass  

    def override_active_lecturer():
        return session.query(User).filter(User.id == user_id).first()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_active_lecturer] = override_active_lecturer

    return app

def test_bank_returns_only_approved(db, db_session_factory):
    ids = _seed_base(db)
    _make_question(db, **_qkw(ids), status="approved", content="Q approved 1")
    _make_question(db, **_qkw(ids), status="approved", content="Q approved 2")
    _make_question(db, **_qkw(ids), status="draft", content="Q draft")
    _make_question(db, **_qkw(ids), status="review_required", content="Q review_required")
    _make_question(db, **_qkw(ids), status="rejected", content="Q rejected")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 2
    for item in data:
        assert item["status"] == "approved"

def test_bank_excludes_draft_and_rejected(db, db_session_factory):
    ids = _seed_base(db)
    _make_question(db, **_qkw(ids), status="draft")
    _make_question(db, **_qkw(ids), status="rejected")
    _make_question(db, **_qkw(ids), status="review_required")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank")

    assert resp.status_code == 200
    data = resp.json()
    assert data == [], f"Expected empty, got {data}"

def test_bank_filter_by_course_id(db, db_session_factory):
    ids = _seed_base(db)

    course2 = Course(
        title="Vật lý",
        code="PHY-001",
        description="",
        created_by=ids["user_id"],
        is_deleted=False,
    )
    db.add(course2)
    db.commit()
    db.refresh(course2)

    material2 = Material(
        title="Chương VL",
        file_path="/tmp/vl.txt",
        status="processed",
        course_id=course2.id,
        uploaded_by=ids["user_id"],
    )
    db.add(material2)
    db.commit()
    db.refresh(material2)

    _make_question(db, material_id=ids["material_id"], course_id=ids["course_id"], status="approved", content="Q course1")
    _make_question(db, material_id=material2.id, course_id=course2.id, status="approved", content="Q course2")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get(f"/questions/bank?course_id={ids['course_id']}")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["course_id"] == ids["course_id"]

def test_bank_filter_by_difficulty(db, db_session_factory):
    ids = _seed_base(db)
    _make_question(db, **_qkw(ids), status="approved", difficulty="easy", content="Q easy")
    _make_question(db, **_qkw(ids), status="approved", difficulty="medium", content="Q medium")
    _make_question(db, **_qkw(ids), status="approved", difficulty="hard", content="Q hard")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank?difficulty=hard")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["difficulty"] == "hard"

def test_bank_filter_by_bloom_level(db, db_session_factory):
    ids = _seed_base(db)
    _make_question(db, **_qkw(ids), status="approved", bloom_level="remember", content="Q remember")
    _make_question(db, **_qkw(ids), status="approved", bloom_level="analyze", content="Q analyze")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank?bloom_level=analyze")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["bloom_level"] == "analyze"

def test_bank_filter_by_question_type(db, db_session_factory):
    ids = _seed_base(db)
    _make_question(db, **_qkw(ids), status="approved", question_type="multiple_choice", content="Q mc")
    _make_question(db, **_qkw(ids), status="approved", question_type="true_false", content="Q tf")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank?question_type=true_false")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["question_type"] == "true_false"

def test_bank_combined_filters(db, db_session_factory):
    ids = _seed_base(db)
    _make_question(db, **_qkw(ids), status="approved", difficulty="easy", bloom_level="remember", question_type="multiple_choice", content="Q match")
    _make_question(db, **_qkw(ids), status="approved", difficulty="hard", bloom_level="remember", question_type="multiple_choice", content="Q no-match difficulty")
    _make_question(db, **_qkw(ids), status="approved", difficulty="easy", bloom_level="analyze", question_type="multiple_choice", content="Q no-match bloom")
    _make_question(db, **_qkw(ids), status="draft", difficulty="easy", bloom_level="remember", question_type="multiple_choice", content="Q no-match status")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank?difficulty=easy&bloom_level=remember&question_type=multiple_choice")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["content"] == "Q match"

def test_bank_empty_when_no_approved(db, db_session_factory):
    ids = _seed_base(db)
    _make_question(db, **_qkw(ids), status="draft")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank")

    assert resp.status_code == 200
    assert resp.json() == []


def test_bank_pagination(db, db_session_factory):
    ids = _seed_base(db)
    for i in range(5):
        _make_question(db, **_qkw(ids), status="approved", content=f"Q {i}")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp_all = client.get("/questions/bank?limit=10")
        resp_page1 = client.get("/questions/bank?skip=0&limit=2")
        resp_page2 = client.get("/questions/bank?skip=2&limit=2")
        resp_page3 = client.get("/questions/bank?skip=4&limit=2")

    assert len(resp_all.json()) == 5
    assert len(resp_page1.json()) == 2
    assert len(resp_page2.json()) == 2
    assert len(resp_page3.json()) == 1

    ids_p1 = {q["id"] for q in resp_page1.json()}
    ids_p2 = {q["id"] for q in resp_page2.json()}
    assert ids_p1.isdisjoint(ids_p2)

def test_bank_requires_auth():
    """Endpoint phải từ chối khi không có auth."""
    app = FastAPI()
    from app.api.routes.question_bank import router as bank_router
    app.include_router(bank_router, prefix="/questions")
    # Không override get_current_active_lecturer → dùng OAuth2 thật → 401
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/questions/bank")
    assert resp.status_code in (401, 403, 422), (
        f"Expected 401/403/422 when unauthenticated, got {resp.status_code}"
    )


def test_bank_ordered_newest_first(db, db_session_factory):
    ids = _seed_base(db)
    q1 = _make_question(db, **_qkw(ids), status="approved", content="Oldest")
    q2 = _make_question(db, **_qkw(ids), status="approved", content="Newest")

    app = _make_app(db_session_factory, user_id=ids["user_id"])
    with TestClient(app) as client:
        resp = client.get("/questions/bank")

    data = resp.json()
    assert data[0]["id"] == q2.id, "Câu mới nhất phải ở đầu danh sách"
