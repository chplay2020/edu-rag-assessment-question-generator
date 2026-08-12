import json

import pytest
from pydantic import ValidationError

from app.ai.generation.output_parser import parse_llm_json_output


def _valid_question_payload():
    return {
        "question_text": "What is virtual memory?",
        "options": [
            {"text": "A memory management technique", "is_correct": True},
            {"text": "A CPU scheduling algorithm", "is_correct": False},
            {"text": "A network protocol", "is_correct": False},
            {"text": "A database index", "is_correct": False},
        ],
        "correct_answer": "A memory management technique",
        "difficulty": "medium",
        "bloom_level": "understand",
        "explanation": "The context describes virtual memory as memory management.",
        "source_chunk_ids": [101],
    }


def test_parse_llm_json_output_batch_object():
    payload = {"questions": [_valid_question_payload()]}

    batch = parse_llm_json_output(json.dumps(payload))

    assert len(batch.questions) == 1
    question = batch.questions[0]
    assert question.question_text == "What is virtual memory?"
    assert question.options[0].is_correct is True
    assert question.source_chunk_ids == [101]


def test_parse_llm_json_output_code_fence():
    raw_output = "```json\n" + json.dumps({"questions": [_valid_question_payload()]}) + "\n```"

    batch = parse_llm_json_output(raw_output)

    assert batch.questions[0].difficulty == "medium"


def test_parse_llm_json_output_single_question_object():
    batch = parse_llm_json_output(json.dumps(_valid_question_payload()))

    assert len(batch.questions) == 1


def test_parse_llm_json_output_rejects_non_json():
    with pytest.raises(ValueError, match="Invalid JSON output"):
        parse_llm_json_output("not json")


def test_parser_rejects_empty_question_text():
    payload = _valid_question_payload()
    payload["question_text"] = " "

    with pytest.raises(ValidationError):
        parse_llm_json_output(json.dumps({"questions": [payload]}))


def test_parser_rejects_not_four_options():
    payload = _valid_question_payload()
    payload["options"] = payload["options"][:3]

    with pytest.raises(ValidationError):
        parse_llm_json_output(json.dumps({"questions": [payload]}))


def test_parser_rejects_multiple_correct_options():
    payload = _valid_question_payload()
    payload["options"][1]["is_correct"] = True

    with pytest.raises(ValidationError, match="exactly one option"):
        parse_llm_json_output(json.dumps({"questions": [payload]}))


def test_parser_rejects_correct_answer_mismatch():
    payload = _valid_question_payload()
    payload["correct_answer"] = "Wrong answer"

    with pytest.raises(ValidationError, match="correct_answer"):
        parse_llm_json_output(json.dumps({"questions": [payload]}))


def test_parser_rejects_invalid_difficulty():
    payload = _valid_question_payload()
    payload["difficulty"] = "impossible"

    with pytest.raises(ValidationError):
        parse_llm_json_output(json.dumps({"questions": [payload]}))


def test_parser_rejects_invalid_bloom_level():
    payload = _valid_question_payload()
    payload["bloom_level"] = "memorize"

    with pytest.raises(ValidationError):
        parse_llm_json_output(json.dumps({"questions": [payload]}))
