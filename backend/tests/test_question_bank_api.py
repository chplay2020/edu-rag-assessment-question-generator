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

# Helpers

def _make_user(db, *, email: str, role: str = "lecturer") -> User:
    user = User(
        email=email,
        hashed_password="x",
        full_name=email.split("@")[0],
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_course(db, *, created_by: int, code: str = "C-001", title: str = "Môn học") -> Course:
    course = Course(
        title=title,
        code=code,
        description="",
        created_by=created_by,
        is_deleted=False,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def _make_material(db, *, course_id: int, uploaded_by: int) -> Material:
    m = Material(
        title="Chương 1",
        file_path="/tmp/ch1.txt",
        status="processed",
        course_id=course_id,
        uploaded_by=uploaded_by,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def _seed_base(db) -> dict:
    """Tạo user, course, material cơ bản. Trả dict có user_id, course_id, material_id."""
    user = _make_user(db, email="lecturer@test.com")
    course = _make_course(db, created_by=user.id, code="MATH-001", title="Toán học")
    material = _make_material(db, course_id=course.id, uploaded_by=user.id)
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


def _make_app(db_session_factory, *, user_id: int) -> FastAPI:
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

# ─── T057 – Các test Question Bank cơ bản ────────────────────────────────────

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

    course2 = _make_course(db, created_by=ids["user_id"], code="PHY-001", title="Vật lý")
    material2 = _make_material(db, course_id=course2.id, uploaded_by=ids["user_id"])

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

# Ownership isolation 

def test_bank_lecturer_cannot_see_other_course(db, db_session_factory):
    """
    T059: Lecturer A không thấy câu hỏi của course do Lecturer B tạo.
    """
    user_a = _make_user(db, email="a@test.com")
    user_b = _make_user(db, email="b@test.com")

    course_a = _make_course(db, created_by=user_a.id, code="CA-001", title="Course A")
    course_b = _make_course(db, created_by=user_b.id, code="CB-001", title="Course B")
    mat_a = _make_material(db, course_id=course_a.id, uploaded_by=user_a.id)
    mat_b = _make_material(db, course_id=course_b.id, uploaded_by=user_b.id)

    _make_question(db, material_id=mat_a.id, course_id=course_a.id, status="approved", content="Q in A")
    _make_question(db, material_id=mat_b.id, course_id=course_b.id, status="approved", content="Q in B")

    # User A gọi API
    app = _make_app(db_session_factory, user_id=user_a.id)
    with TestClient(app) as client:
        resp = client.get("/questions/bank")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1, f"Lecturer A phải chỉ thấy 1 câu hỏi của mình, nhưng thấy {len(data)}"
    assert data[0]["content"] == "Q in A"
    assert data[0]["course_id"] == course_a.id


def test_bank_admin_sees_all_courses(db, db_session_factory):
    """
    T059: Admin thấy câu hỏi approved từ tất cả các course.
    """
    admin = _make_user(db, email="admin@test.com", role="admin")
    lect_a = _make_user(db, email="la@test.com")
    lect_b = _make_user(db, email="lb@test.com")

    course_a = _make_course(db, created_by=lect_a.id, code="A-001", title="Course A")
    course_b = _make_course(db, created_by=lect_b.id, code="B-001", title="Course B")
    mat_a = _make_material(db, course_id=course_a.id, uploaded_by=lect_a.id)
    mat_b = _make_material(db, course_id=course_b.id, uploaded_by=lect_b.id)

    _make_question(db, material_id=mat_a.id, course_id=course_a.id, status="approved", content="Q A1")
    _make_question(db, material_id=mat_b.id, course_id=course_b.id, status="approved", content="Q B1")
    _make_question(db, material_id=mat_b.id, course_id=course_b.id, status="draft", content="Q B draft")

    app = _make_app(db_session_factory, user_id=admin.id)
    with TestClient(app) as client:
        resp = client.get("/questions/bank")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2, "Admin phải thấy 2 câu approved từ 2 course khác nhau"
    statuses = {d["status"] for d in data}
    assert statuses == {"approved"}, "Admin chỉ thấy câu approved dù thấy nhiều course"


def test_bank_filters_dont_expose_other_lecturer_questions(db, db_session_factory):
    """
    T059: Filter difficulty/bloom không làm lộ câu hỏi của lecturer khác.
    """
    user_a = _make_user(db, email="fa@test.com")
    user_b = _make_user(db, email="fb@test.com")

    course_a = _make_course(db, created_by=user_a.id, code="FA-001", title="FA")
    course_b = _make_course(db, created_by=user_b.id, code="FB-001", title="FB")
    mat_a = _make_material(db, course_id=course_a.id, uploaded_by=user_a.id)
    mat_b = _make_material(db, course_id=course_b.id, uploaded_by=user_b.id)

    # Cả 2 đều có câu approved difficulty=hard
    _make_question(db, material_id=mat_a.id, course_id=course_a.id, status="approved", difficulty="hard", content="A hard")
    _make_question(db, material_id=mat_b.id, course_id=course_b.id, status="approved", difficulty="hard", content="B hard")

    # User A lọc theo difficulty=hard → chỉ thấy câu của mình
    app = _make_app(db_session_factory, user_id=user_a.id)
    with TestClient(app) as client:
        resp = client.get("/questions/bank?difficulty=hard")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["content"] == "A hard"

# Export helper (get_exportable_questions)

def test_exportable_returns_approved_ids(db):
    """get_exportable_questions trả về câu approved của đúng user."""
    from app.services.question_bank_service import get_exportable_questions

    user = _make_user(db, email="exp@test.com")
    course = _make_course(db, created_by=user.id, code="EXP-001", title="Export Course")
    mat = _make_material(db, course_id=course.id, uploaded_by=user.id)

    q1 = _make_question(db, material_id=mat.id, course_id=course.id, status="approved", content="Exp Q1")
    q2 = _make_question(db, material_id=mat.id, course_id=course.id, status="approved", content="Exp Q2")

    result = get_exportable_questions(db, current_user=user, question_ids=[q1.id, q2.id])
    assert len(result) == 2
    for q in result:
        assert q.status == "approved"


def test_exportable_rejects_draft_ids(db):
    """get_exportable_questions raise HTTP 422 nếu có câu draft trong danh sách."""
    from fastapi import HTTPException
    from app.services.question_bank_service import get_exportable_questions

    user = _make_user(db, email="exp2@test.com")
    course = _make_course(db, created_by=user.id, code="EXP-002", title="Exp2")
    mat = _make_material(db, course_id=course.id, uploaded_by=user.id)

    approved = _make_question(db, material_id=mat.id, course_id=course.id, status="approved", content="OK")
    draft = _make_question(db, material_id=mat.id, course_id=course.id, status="draft", content="Draft")

    with pytest.raises(HTTPException) as exc_info:
        get_exportable_questions(db, current_user=user, question_ids=[approved.id, draft.id])

    assert exc_info.value.status_code == 422
    detail = exc_info.value.detail
    assert draft.id in detail["invalid_question_ids"]
    assert approved.id not in detail["invalid_question_ids"]


def test_exportable_rejects_rejected_ids(db):
    """get_exportable_questions raise HTTP 422 nếu có câu rejected."""
    from fastapi import HTTPException
    from app.services.question_bank_service import get_exportable_questions

    user = _make_user(db, email="exp3@test.com")
    course = _make_course(db, created_by=user.id, code="EXP-003", title="Exp3")
    mat = _make_material(db, course_id=course.id, uploaded_by=user.id)

    rejected = _make_question(db, material_id=mat.id, course_id=course.id, status="rejected", content="Rejected")

    with pytest.raises(HTTPException) as exc_info:
        get_exportable_questions(db, current_user=user, question_ids=[rejected.id])

    assert exc_info.value.status_code == 422
    assert rejected.id in exc_info.value.detail["invalid_question_ids"]


def test_exportable_rejects_other_lecturer_ids(db):
    """get_exportable_questions không cho phép export câu của lecturer khác."""
    from fastapi import HTTPException
    from app.services.question_bank_service import get_exportable_questions

    user_a = _make_user(db, email="oa@test.com")
    user_b = _make_user(db, email="ob@test.com")

    course_b = _make_course(db, created_by=user_b.id, code="OB-001", title="Course B")
    mat_b = _make_material(db, course_id=course_b.id, uploaded_by=user_b.id)
    q_b = _make_question(db, material_id=mat_b.id, course_id=course_b.id, status="approved", content="B's Q")

    # User A cố export câu của B → phải bị từ chối
    with pytest.raises(HTTPException) as exc_info:
        get_exportable_questions(db, current_user=user_a, question_ids=[q_b.id])

    assert exc_info.value.status_code == 422
    assert q_b.id in exc_info.value.detail["invalid_question_ids"]


def test_exportable_empty_list(db):
    """get_exportable_questions với list rỗng trả về list rỗng, không lỗi."""
    from app.services.question_bank_service import get_exportable_questions

    user = _make_user(db, email="empty@test.com")
    result = get_exportable_questions(db, current_user=user, question_ids=[])
    assert result == []


def test_exportable_nonexistent_id_raises(db):
    """get_exportable_questions raise 422 nếu ID không tồn tại."""
    from fastapi import HTTPException
    from app.services.question_bank_service import get_exportable_questions

    user = _make_user(db, email="ne@test.com")

    with pytest.raises(HTTPException) as exc_info:
        get_exportable_questions(db, current_user=user, question_ids=[99999])

    assert exc_info.value.status_code == 422
    assert 99999 in exc_info.value.detail["invalid_question_ids"]
