import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import io

from app.main import app
from app.api.deps import get_db, get_current_user_id, get_current_user_role, get_current_active_lecturer
from app.models import Base
from app.models.user import User
from app.models.course import Course
from app.workers import material_worker, question_worker

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

@pytest.fixture()
def client(db_session_factory, monkeypatch, tmp_path):
    session = db_session_factory()
    
    # Mock SessionLocal for workers
    monkeypatch.setattr(material_worker, "SessionLocal", db_session_factory)
    monkeypatch.setattr(question_worker, "SessionLocal", db_session_factory)

    # Set processed dir
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))
    
    user = User(
        email="testlecturer@example.com",
        hashed_password="hash",
        full_name="Lecturer",
        role="lecturer",
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    def override_db():
        try:
            yield session
        finally:
            pass

    def override_active_lecturer():
        return user

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_active_lecturer] = override_active_lecturer
    app.dependency_overrides[get_current_user_id] = lambda: user.id
    app.dependency_overrides[get_current_user_role] = lambda: user.role

    # Mock background tasks to run synchronously
    from fastapi import BackgroundTasks
    original_add_task = BackgroundTasks.add_task
    def sync_add_task(self, func, *args, **kwargs):
        func(*args, **kwargs)
    monkeypatch.setattr(BackgroundTasks, "add_task", sync_add_task)

    # Mock embeddings and qdrant
    monkeypatch.setattr(material_worker, "embed_texts", lambda texts: [[0.1]*1536 for _ in texts])
    
    class FakeVectorStore:
        def ensure_collections(self): pass
        def upsert_material_chunks(self, chunks, vectors): pass
        def upsert_question_vectors(self, questions, vectors): pass
        def search_material_chunks(self, *args, **kwargs): return []
        def search_questions(self, *args, **kwargs): return []

    monkeypatch.setattr(material_worker, "get_vector_store", lambda: FakeVectorStore())
    monkeypatch.setattr(question_worker, "get_vector_store", lambda: FakeVectorStore())

    # Need to override pipeline.generate_questions_for_material so it doesn't call LLM
    from app.ai import pipeline
    from app.ai.generation.output_parser import GeneratedQuestion, GeneratedOption
    def fake_generate(*args, **kwargs):
        outcome = pipeline.GenerationOutcome()
        # Create a fake candidate
        q = GeneratedQuestion(
            question_text="Fake generated question?",
            options=[
                GeneratedOption(text="A", is_correct=True),
                GeneratedOption(text="B", is_correct=False),
                GeneratedOption(text="C", is_correct=False),
                GeneratedOption(text="D", is_correct=False),
            ],
            difficulty="medium",
            bloom_level="remember",
            explanation="Because",
            source_chunk_ids=[],
            correct_answer="A"
        )
        from app.ai.validation.question_validator import ValidationResult
        candidate = pipeline.QuestionCandidate(
            question=q,
            status=pipeline.STATUS_REVIEW_REQUIRED,
            validation=ValidationResult(is_valid=True)
        )
        outcome.candidates.append(candidate)
        return outcome
    
    monkeypatch.setattr(pipeline, "generate_questions_for_material", fake_generate)

    with TestClient(app) as c:
        yield c

def test_full_flow(client, db):
    course = Course(title="Test Course", code="TEST-01", description="", created_by=1, is_deleted=False)
    db.add(course)
    db.commit()
    db.refresh(course)

    # 1. Upload Material
    file_content = b"This is a test document."
    response = client.post(
        "/api/v1/materials/upload",
        data={"course_id": course.id},
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200, response.json()
    material_id = response.json()["id"]

    # 2. Process Material (this will trigger background worker synchronously due to mock)
    process_resp = client.post(f"/api/v1/materials/{material_id}/process")
    assert process_resp.status_code == 202
    
    # 3. Generate Questions (trigger background worker synchronously)
    gen_resp = client.post(
        f"/api/v1/jobs/material/{material_id}/generate-questions",
        json={"number_of_questions": 1, "difficulty": "medium", "language": "vi"}
    )
    assert gen_resp.status_code == 200

    # 4. Get questions (they should be review_required)
    questions_resp = client.get(f"/api/v1/questions?course_id={course.id}")
    assert questions_resp.status_code == 200
    questions = questions_resp.json()
    assert len(questions) > 0
    q_id = questions[0]["id"]

    # 5. Review Question
    review_resp = client.post(f"/api/v1/questions/{q_id}/review", json={"status": "approved", "feedback": "Looks good"})
    assert review_resp.status_code == 200

    # 6. Export to Word
    export_resp = client.post("/api/v1/exports/word", json={"question_ids": [q_id]})
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
