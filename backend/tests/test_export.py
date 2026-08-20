from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import openpyxl
import io
from app.main import app
from app.models import Base
from app.models.user import User
from app.models.course import Course
from app.models.material import Material
from app.models.question import Question, Option
from app.services.export_service import generate_excel_workbook, _sanitize_for_excel
from tests.test_question_bank_api import _make_user

client = TestClient(app)

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

@pytest.fixture(autouse=True)
def override_deps(db_session_factory):
    from app.api.deps import get_db
    def override_db():
        session = db_session_factory()
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()

# Helper fixtures
@pytest.fixture
def lecturer_user(db):
    user = _make_user(db, email="lecturer_export@test.com", role="lecturer")
    return user

@pytest.fixture
def other_lecturer_user(db):
    return _make_user(db, email="other_lecturer_export@test.com", role="lecturer")

@pytest.fixture
def test_course(db, lecturer_user):
    c = Course(title="Export Course", created_by=lecturer_user.id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@pytest.fixture
def test_material(db, test_course, lecturer_user):
    m = Material(
        title="Test Material Source",
        file_path="/fake/path",
        course_id=test_course.id,
        uploaded_by=lecturer_user.id
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def _create_question(db, course_id, material_id, content, status="approved", diff="medium", num_opts=4, correct_idx=0):
    q = Question(
        course_id=course_id,
        material_id=material_id,
        content=content,
        status=status,
        difficulty=diff,
        bloom_level="remember",
        question_type="multiple_choice",
        explanation=f"Giải thích cho {content}"
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    
    # Adding options
    for i in range(num_opts):
        opt = Option(
            question_id=q.id,
            content=f"Option {i} for {content}",
            is_correct=(i == correct_idx)
        )
        db.add(opt)
    db.commit()
    return q

# Unit tests for _sanitize_for_excel
def test_sanitize_for_excel():
    assert _sanitize_for_excel(None) == ""
    assert _sanitize_for_excel("") == ""
    assert _sanitize_for_excel("Hello") == "Hello"
    assert _sanitize_for_excel("1+1") == "1+1"
    assert _sanitize_for_excel("=SUM(A1:A2)") == "'=SUM(A1:A2)"
    assert _sanitize_for_excel("+123") == "'+123"
    assert _sanitize_for_excel("-456") == "'-456"
    assert _sanitize_for_excel("@something") == "'@something"

# Unit tests for workbook generation
def test_generate_excel_workbook_empty():
    stream = generate_excel_workbook([])
    wb = openpyxl.load_workbook(stream)
    assert "Câu hỏi" in wb.sheetnames
    ws = wb["Câu hỏi"]
    assert ws.max_row == 1
    # Check default headers up to D
    headers = [cell.value for cell in ws[1]]
    assert "Đáp án D" in headers
    assert "Đáp án E" not in headers

def test_generate_excel_workbook_with_data(db, test_course, test_material):
    q1 = _create_question(db, test_course.id, test_material.id, "Lịch sử Tiếng Việt") 
    q2 = _create_question(db, test_course.id, test_material.id, "=Formula injection", num_opts=2) 
    q3 = _create_question(db, test_course.id, test_material.id, "Extra opts", num_opts=5, correct_idx=4) # > 4 opts, answer E
    
    db.refresh(q1)
    db.refresh(q2)
    db.refresh(q3)
    
    questions = [q1, q2, q3]
    
    stream = generate_excel_workbook(questions)
    wb = openpyxl.load_workbook(stream)
    ws = wb["Câu hỏi"]
    
    assert ws.max_row == 4 # 1 header + 3 rows
    
    headers = [cell.value for cell in ws[1]]
    assert "Đáp án E" in headers # dynamic column created
    
    # Check Q1 (Unicode and Source)
    assert ws.cell(row=2, column=2).value == "Lịch sử Tiếng Việt"
    assert ws.cell(row=2, column=8).value == "A" # A is correct in column 8
    assert ws.cell(row=2, column=13).value == test_material.title # Nguồn is at 13 now (STT, Nội dung, A, B, C, D, E, Đáp án đúng, Giải thích, Độ khó, Bloom, Loại, Nguồn) -> 13
    
    # Check Q2 (< 4 opts and injection)
    assert ws.cell(row=3, column=2).value == "'=Formula injection"
    assert ws.cell(row=3, column=3).value == "Option 0 for =Formula injection"
    assert ws.cell(row=3, column=4).value == "Option 1 for =Formula injection"
    assert ws.cell(row=3, column=5).value is None or ws.cell(row=3, column=5).value == "" # missing C
    assert ws.cell(row=3, column=8).value == "A" # A correct
    
    # Check Q3 (Extra opts)
    assert ws.cell(row=4, column=7).value == "Option 4 for Extra opts" # E
    assert ws.cell(row=4, column=8).value == "E" # correct is E

# API Integration tests
def get_auth_headers(user: User):
    from app.core.security import create_access_token
    token = create_access_token(user.email)
    return {"Authorization": f"Bearer {token}"}

def test_api_export_excel_success(db, lecturer_user, test_course, test_material):
    q1 = _create_question(db, test_course.id, test_material.id, "Q1")
    q2 = _create_question(db, test_course.id, test_material.id, "Q2")
    q3 = _create_question(db, test_course.id, test_material.id, "Q3")
    
    headers = get_auth_headers(lecturer_user)
    
    # Request out of order, and with duplicates
    request_data = {"question_ids": [q3.id, q1.id, q3.id, q2.id]}
    
    response = client.post("/api/v1/exports/excel", json=request_data, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=questions_export" in response.headers["content-disposition"]
    
    # Read response as Excel
    stream = io.BytesIO(response.content)
    wb = openpyxl.load_workbook(stream)
    ws = wb.active
    
    # Should have 3 rows of data (no duplicates)
    assert ws.max_row == 4
    
    # Order should be Q3, Q1, Q2
    assert ws.cell(row=2, column=2).value == "Q3"
    assert ws.cell(row=3, column=2).value == "Q1"
    assert ws.cell(row=4, column=2).value == "Q2"

def test_api_export_excel_unauthorized():
    response = client.post("/api/v1/exports/excel", json={"question_ids": [1]})
    assert response.status_code == 401

def test_api_export_excel_empty_list(lecturer_user):
    headers = get_auth_headers(lecturer_user)
    response = client.post("/api/v1/exports/excel", json={"question_ids": []}, headers=headers)
    assert response.status_code == 422 # Pydantic validation

def test_api_export_excel_invalid_ids(db, lecturer_user, other_lecturer_user, test_course, test_material):
    # Draft question
    q_draft = _create_question(db, test_course.id, test_material.id, "Draft", status="draft")
    
    # Other's question
    other_course = Course(title="Other", created_by=other_lecturer_user.id)
    db.add(other_course)
    db.commit()
    db.refresh(other_course)
    q_other = _create_question(db, other_course.id, test_material.id, "Other")
    
    # Approved question
    q_valid = _create_question(db, test_course.id, test_material.id, "Valid")
    
    headers = get_auth_headers(lecturer_user)
    
    response = client.post("/api/v1/exports/excel", json={"question_ids": [q_draft.id, q_other.id, q_valid.id, 99999]}, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "invalid_question_ids" in data["message"]
    invalid_ids = data["message"]["invalid_question_ids"]
    assert set(invalid_ids) == {q_draft.id, q_other.id, 99999}
    assert q_valid.id not in invalid_ids
