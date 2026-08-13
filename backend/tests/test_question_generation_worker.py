import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.generation.output_parser import GeneratedQuestionBatch
from app.api.routes import jobs
from app.models import Base
from app.models.course import Course
from app.models.material import Chunk, Job, Material
from app.models.question import Option, Question
from app.models.user import User
from app.services import question_generation_service
from app.workers import question_worker


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


def _seed_material(
    db_session_factory,
    *,
    material_status: str = "processed",
) -> tuple[int, int, int]:
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
        title="Operating Systems",
        code="OS-101",
        description="",
        created_by=user.id,
        is_deleted=False,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    material = Material(
        title="Process and memory management",
        file_path="storage/uploads/os.txt",
        status=material_status,
        course_id=course.id,
        uploaded_by=user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    chunk = Chunk(
        material_id=material.id,
        content="Operating systems manage processes, memory, and hardware resources.",
        chunk_index=0,
    )
    db.add(chunk)
    db.commit()

    ids = (user.id, course.id, material.id)
    db.close()
    return ids


def _create_generation_job(db_session_factory, material_id: int) -> int:
    db = db_session_factory()
    job = Job(
        material_id=material_id,
        task_type="generate_questions",
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()
    return job_id


def _generated_batch() -> GeneratedQuestionBatch:
    return GeneratedQuestionBatch.model_validate(
        {
            "questions": [
                {
                    "question_text": "What do operating systems manage?",
                    "options": [
                        {"text": "Processes, memory, and hardware resources", "is_correct": True},
                        {"text": "Only web browsers", "is_correct": False},
                        {"text": "Only databases", "is_correct": False},
                        {"text": "Only social networks", "is_correct": False},
                    ],
                    "correct_answer": "Processes, memory, and hardware resources",
                    "difficulty": "easy",
                    "bloom_level": "remember",
                    "explanation": "The context states that operating systems manage these resources.",
                    "source_chunk_ids": [1],
                }
            ]
        }
    )


def _mock_ai_pipeline(monkeypatch):
    calls = {"retrieve": False, "generate": False}

    def fake_retrieve_context(query, material_id=None, course_id=None, top_k=5):
        calls["retrieve"] = True
        return [
            {
                "chunk_id": 1,
                "material_id": material_id,
                "course_id": course_id,
                "content": "Operating systems manage processes, memory, and hardware resources.",
                "score": 1.0,
                "payload": {"chunk_id": 1},
            }
        ]

    def fake_generate_questions(*args, **kwargs):
        calls["generate"] = True
        return _generated_batch()

    monkeypatch.setattr(question_worker.retriever, "retrieve_context", fake_retrieve_context)
    monkeypatch.setattr(
        question_worker.question_generator,
        "generate_questions",
        fake_generate_questions,
    )
    return calls


def test_service_does_not_create_job_if_material_not_processed(db_session_factory):
    user_id, _course_id, material_id = _seed_material(
        db_session_factory,
        material_status="uploaded",
    )
    db = db_session_factory()

    with pytest.raises(HTTPException) as exc_info:
        question_generation_service.create_question_generation_job(
            db=db,
            material_id=material_id,
            current_user_id=user_id,
            current_user_role="lecturer",
        )

    assert exc_info.value.status_code == 409
    assert db.query(Job).count() == 0
    db.close()


def test_service_creates_pending_generate_questions_job(db_session_factory):
    user_id, _course_id, material_id = _seed_material(db_session_factory)
    db = db_session_factory()

    job = question_generation_service.create_question_generation_job(
        db=db,
        material_id=material_id,
        current_user_id=user_id,
        current_user_role="lecturer",
    )

    assert job.task_type == "generate_questions"
    assert job.status == "pending"
    assert job.material_id == material_id
    db.close()


def test_worker_success_saves_questions_options_and_marks_job_done(
    monkeypatch,
    db_session_factory,
):
    monkeypatch.setattr(question_worker, "SessionLocal", db_session_factory)
    _user_id, _course_id, material_id = _seed_material(db_session_factory)
    job_id = _create_generation_job(db_session_factory, material_id)
    calls = _mock_ai_pipeline(monkeypatch)

    question_worker.process_question_generation_job(job_id, number_of_questions=1)

    db = db_session_factory()
    job = db.query(Job).filter(Job.id == job_id).first()
    questions = db.query(Question).filter(Question.material_id == material_id).all()
    options = db.query(Option).filter(Option.question_id == questions[0].id).all()
    db.close()

    assert calls == {"retrieve": True, "generate": True}
    assert job is not None
    assert job.status == "done"
    assert len(questions) == 1
    assert questions[0].content == "What do operating systems manage?"
    assert questions[0].status == "draft"
    assert questions[0].source_chunk_ids == [1]
    assert len(options) == 4
    assert sum(option.is_correct for option in options) == 1


def test_worker_marks_question_review_required_when_validation_warns(
    monkeypatch,
    db_session_factory,
):
    monkeypatch.setattr(question_worker, "SessionLocal", db_session_factory)
    _user_id, _course_id, material_id = _seed_material(db_session_factory)
    job_id = _create_generation_job(db_session_factory, material_id)
    _mock_ai_pipeline(monkeypatch)

    original_validate_questions = question_worker.question_validator.validate_questions

    def fake_validate_questions(batch):
        results = original_validate_questions(batch)
        results[0].warnings.append("manual review")
        return results

    monkeypatch.setattr(
        question_worker.question_validator,
        "validate_questions",
        fake_validate_questions,
    )

    question_worker.process_question_generation_job(job_id, number_of_questions=1)

    db = db_session_factory()
    question = db.query(Question).filter(Question.material_id == material_id).first()
    db.close()

    assert question is not None
    assert question.status == "review_required"


def test_worker_marks_job_failed_when_generation_raises(
    monkeypatch,
    db_session_factory,
):
    monkeypatch.setattr(question_worker, "SessionLocal", db_session_factory)
    _user_id, _course_id, material_id = _seed_material(db_session_factory)
    job_id = _create_generation_job(db_session_factory, material_id)
    monkeypatch.setattr(
        question_worker.retriever,
        "retrieve_context",
        lambda *args, **kwargs: [],
    )

    def raise_generation_error(*args, **kwargs):
        raise RuntimeError("generator failed")

    monkeypatch.setattr(
        question_worker.question_generator,
        "generate_questions",
        raise_generation_error,
    )

    with pytest.raises(RuntimeError, match="generator failed"):
        question_worker.process_question_generation_job(job_id)

    db = db_session_factory()
    job = db.query(Job).filter(Job.id == job_id).first()
    question_count = db.query(Question).count()
    db.close()

    assert job is not None
    assert job.status == "failed"
    assert question_count == 0


def test_worker_fails_if_material_not_processed(monkeypatch, db_session_factory):
    monkeypatch.setattr(question_worker, "SessionLocal", db_session_factory)
    _user_id, _course_id, material_id = _seed_material(
        db_session_factory,
        material_status="uploaded",
    )
    job_id = _create_generation_job(db_session_factory, material_id)

    with pytest.raises(question_worker.QuestionGenerationError):
        question_worker.process_question_generation_job(job_id)

    db = db_session_factory()
    job = db.query(Job).filter(Job.id == job_id).first()
    question_count = db.query(Question).count()
    db.close()

    assert job is not None
    assert job.status == "failed"
    assert question_count == 0


def test_generate_questions_endpoint_exists():
    matching_routes = [
        route
        for route in jobs.router.routes
        if getattr(route, "path", None) == "/material/{material_id}/generate-questions"
        and "POST" in getattr(route, "methods", set())
    ]

    assert matching_routes
