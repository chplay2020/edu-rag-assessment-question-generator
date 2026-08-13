from datetime import datetime, timezone

from app.models.question import Question
from app.schemas.question_schema import QuestionCreate, QuestionResponse


def test_question_create_uses_model_field_names():
    payload = QuestionCreate(
        material_id=1,
        course_id=2,
        content="What is parent-child chunking?",
        difficulty="medium",
        bloom_level="understand",
        explanation="It separates retrieval units from context units.",
        source_chunk_ids=[11, 12],
        options=[
            {"content": "A chunking strategy", "is_correct": True},
            {"content": "A grading rubric", "is_correct": False},
        ],
    )

    assert payload.difficulty == "medium"
    assert payload.bloom_level == "understand"
    assert payload.source_chunk_ids == [11, 12]
    assert not hasattr(payload, "difficulty_level")
    assert not hasattr(payload, "blooms_taxonomy")


def test_question_response_accepts_source_chunk_ids_from_model():
    created_at = datetime.now(timezone.utc)
    question = Question(
        id=5,
        material_id=1,
        course_id=2,
        content="What does RAG add to question generation?",
        difficulty="hard",
        bloom_level="analyze",
        question_type="multiple_choice",
        explanation="It grounds generation in retrieved context.",
        source_chunk_ids=[101, 102],
        status="review_required",
        created_at=created_at,
    )

    response = QuestionResponse.model_validate(question)

    assert response.content == question.content
    assert response.difficulty == "hard"
    assert response.bloom_level == "analyze"
    assert response.source_chunk_ids == [101, 102]
    assert response.status == "review_required"
