from app.ai.generation.output_parser import GeneratedQuestionBatch
from app.ai.validation.question_validator import validate_question, validate_questions


def _valid_question(source_chunk_ids=None):
    return {
        "question_text": "Hệ điều hành quản lý thành phần nào?",
        "options": [
            {"text": "Tiến trình, bộ nhớ và tài nguyên phần cứng", "is_correct": True},
            {"text": "Chỉ trình duyệt web", "is_correct": False},
            {"text": "Chỉ cơ sở dữ liệu", "is_correct": False},
            {"text": "Chỉ mạng xã hội", "is_correct": False},
        ],
        "correct_answer": "Tiến trình, bộ nhớ và tài nguyên phần cứng",
        "difficulty": "easy",
        "bloom_level": "remember",
        "explanation": "Ngữ cảnh nêu hệ điều hành quản lý tiến trình, bộ nhớ và tài nguyên.",
        "source_chunk_ids": [1] if source_chunk_ids is None else source_chunk_ids,
    }


def test_validate_question_accepts_valid_question():
    result = validate_question(_valid_question())

    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings == []
    assert result.scores["format"] == 1.0


def test_validate_question_rejects_empty_question_text():
    question = _valid_question()
    question["question_text"] = " "

    result = validate_question(question)

    assert result.is_valid is False
    assert "question_text/content must not be empty" in result.errors


def test_validate_question_rejects_wrong_option_count():
    question = _valid_question()
    question["options"] = question["options"][:3]

    result = validate_question(question)

    assert result.is_valid is False
    assert "MCQ must have exactly 4 options" in result.errors


def test_validate_question_rejects_multiple_correct_options():
    question = _valid_question()
    question["options"][1]["is_correct"] = True

    result = validate_question(question)

    assert result.is_valid is False
    assert "MCQ must have exactly 1 correct option" in result.errors


def test_validate_question_rejects_correct_answer_mismatch():
    question = _valid_question()
    question["correct_answer"] = "Sai"

    result = validate_question(question)

    assert result.is_valid is False
    assert "correct_answer must match the correct option text" in result.errors


def test_validate_question_rejects_invalid_difficulty_and_bloom():
    question = _valid_question()
    question["difficulty"] = "impossible"
    question["bloom_level"] = "memorize"

    result = validate_question(question)

    assert result.is_valid is False
    assert "difficulty must be one of easy, medium, hard" in result.errors
    assert any("bloom_level must be one of" in error for error in result.errors)


def test_validate_question_warns_when_source_chunks_empty():
    result = validate_question(_valid_question(source_chunk_ids=[]))

    assert result.is_valid is True
    assert "source_chunk_ids is empty" in result.warnings
    assert result.scores["grounding"] == 0.5


def test_validate_questions_accepts_batch_object():
    batch = GeneratedQuestionBatch.model_validate({"questions": [_valid_question()]})

    results = validate_questions(batch)

    assert len(results) == 1
    assert results[0].is_valid is True


def test_validate_question_accepts_db_style_content_fields():
    question = {
        "content": "Hệ điều hành là gì?",
        "options": [
            {"content": "Phần mềm quản lý tài nguyên máy tính", "is_correct": True},
            {"content": "Một thiết bị phần cứng", "is_correct": False},
            {"content": "Một giao thức mạng", "is_correct": False},
            {"content": "Một loại cơ sở dữ liệu", "is_correct": False},
        ],
        "correct_answer": "Phần mềm quản lý tài nguyên máy tính",
        "difficulty": "easy",
        "bloom_level": "remember",
        "explanation": "Câu trả lời dựa trên định nghĩa trong ngữ cảnh.",
        "source_chunk_ids": [3],
    }

    result = validate_question(question)

    assert result.is_valid is True
