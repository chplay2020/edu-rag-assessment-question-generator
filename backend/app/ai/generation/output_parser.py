import json
import re
from typing import Any, Literal, TypeAlias, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


Difficulty: TypeAlias = Literal["easy", "medium", "hard"]
BloomLevel: TypeAlias = Literal[
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]

DIFFICULTY_VALUES = ("easy", "medium", "hard")
BLOOM_VALUES = (
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
)

# Schema OpenAPI-subset gửi kèm request Gemini (JSON mode). Nhờ nó model trả
# đúng cấu trúc ngay từ lần đầu thay vì phải retry vì sai format.
MCQ_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "question_text": {"type": "STRING"},
                    "options": {
                        "type": "ARRAY",
                        "minItems": 4,
                        "maxItems": 4,
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "text": {"type": "STRING"},
                                "is_correct": {"type": "BOOLEAN"},
                            },
                            "required": ["text", "is_correct"],
                            "propertyOrdering": ["text", "is_correct"],
                        },
                    },
                    "correct_answer": {"type": "STRING"},
                    "difficulty": {"type": "STRING", "enum": list(DIFFICULTY_VALUES)},
                    "bloom_level": {"type": "STRING", "enum": list(BLOOM_VALUES)},
                    "explanation": {"type": "STRING"},
                    "source_chunk_ids": {
                        "type": "ARRAY",
                        "items": {"type": "INTEGER"},
                    },
                },
                "required": [
                    "question_text",
                    "options",
                    "correct_answer",
                    "difficulty",
                    "bloom_level",
                    "explanation",
                    "source_chunk_ids",
                ],
                "propertyOrdering": [
                    "question_text",
                    "options",
                    "correct_answer",
                    "difficulty",
                    "bloom_level",
                    "explanation",
                    "source_chunk_ids",
                ],
            },
        }
    },
    "required": ["questions"],
}


class GeneratedOption(BaseModel):
    text: str
    is_correct: bool

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("option text must not be empty")
        return value


class GeneratedQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str
    options: list[GeneratedOption] = Field(min_length=4, max_length=4)
    correct_answer: str
    difficulty: Difficulty
    bloom_level: BloomLevel
    explanation: str
    source_chunk_ids: list[int] = Field(default_factory=list)

    @field_validator("question_text", "correct_answer", "explanation")
    @classmethod
    def string_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must not be empty")
        return value

    @model_validator(mode="after")
    def validate_mcq_contract(self) -> "GeneratedQuestion":
        correct_options = [option for option in self.options if option.is_correct]
        if len(correct_options) != 1:
            raise ValueError("exactly one option must be correct")

        correct_answer = self.correct_answer.strip()
        if correct_options[0].text != correct_answer:
            raise ValueError("correct_answer must match the correct option text")

        return self


class GeneratedQuestionBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[GeneratedQuestion] = Field(default_factory=list)


def _strip_json_code_fence(raw_output: str) -> str:
    text = raw_output.strip()
    fenced_match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
    if fenced_match:
        return cast(str, fenced_match.group(1)).strip()
    return text


def _extract_json_block(text: str) -> str | None:
    """Bóc khối JSON đầu tiên khi model lỡ kèm thêm lời dẫn quanh JSON."""
    for opening, closing in (("{", "}"), ("[", "]")):
        start = text.find(opening)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
    return None


def _normalize_json_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        return {"questions": payload}
    if isinstance(payload, dict):
        if "questions" in payload:
            return payload
        if "question_text" in payload:
            return {"questions": [payload]}
    raise ValueError("LLM output must be a question object, list, or batch object")


def _loads(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        block = _extract_json_block(text)
        if block is None:
            raise ValueError(f"Invalid JSON output: {exc}") from exc
        try:
            return json.loads(block)
        except json.JSONDecodeError as inner_exc:
            raise ValueError(f"Invalid JSON output: {inner_exc}") from inner_exc


def parse_llm_json_output(raw_output: str) -> GeneratedQuestionBatch:
    """Parse nghiêm ngặt: một câu hỏi sai làm hỏng cả batch.

    Dùng khi cần chắc chắn toàn bộ output hợp lệ (test hợp đồng schema).
    """
    payload = _loads(_strip_json_code_fence(raw_output))
    normalized_payload = _normalize_json_payload(payload)
    return GeneratedQuestionBatch.model_validate(normalized_payload)


def _describe_validation_error(exc: ValidationError) -> str:
    parts = []
    for error in exc.errors():
        location = ".".join(str(item) for item in error.get("loc", ()))
        parts.append(f"{location}: {error.get('msg')}" if location else str(error.get("msg")))
    return "; ".join(parts) or str(exc)


def parse_questions_lenient(
    raw_output: str,
) -> tuple[list[GeneratedQuestion], list[str]]:
    """Parse "cứu vãn": giữ lại các câu hỏi hợp lệ, bỏ câu hỏng.

    Đây là chế độ pipeline dùng khi sinh câu hỏi. Nếu model trả 5 câu mà 1 câu
    sai định dạng thì giữ 4 câu tốt và sinh bù 1 câu, thay vì fail cả job.

    Trả về `(danh sách câu hợp lệ, danh sách mô tả lỗi)`.
    """
    errors: list[str] = []
    try:
        payload = _loads(_strip_json_code_fence(raw_output))
    except ValueError as exc:
        return [], [str(exc)]

    try:
        normalized_payload = _normalize_json_payload(payload)
    except ValueError as exc:
        return [], [str(exc)]

    raw_questions = normalized_payload.get("questions")
    if not isinstance(raw_questions, list):
        return [], ["'questions' phải là một mảng"]

    questions: list[GeneratedQuestion] = []
    for index, raw_question in enumerate(raw_questions):
        try:
            questions.append(GeneratedQuestion.model_validate(raw_question))
        except ValidationError as exc:
            errors.append(f"question[{index}] không hợp lệ: {_describe_validation_error(exc)}")
        except Exception as exc:
            errors.append(f"question[{index}] không hợp lệ: {exc}")

    return questions, errors


__all__ = [
    "BLOOM_VALUES",
    "DIFFICULTY_VALUES",
    "GeneratedOption",
    "GeneratedQuestion",
    "GeneratedQuestionBatch",
    "MCQ_RESPONSE_SCHEMA",
    "parse_llm_json_output",
    "parse_questions_lenient",
]
