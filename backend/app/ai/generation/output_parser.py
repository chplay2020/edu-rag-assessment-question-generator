import json
import re
from typing import Any, Literal, TypeAlias, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Difficulty: TypeAlias = Literal["easy", "medium", "hard"]
BloomLevel: TypeAlias = Literal[
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]


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


def _normalize_json_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        return {"questions": payload}
    if isinstance(payload, dict):
        if "questions" in payload:
            return payload
        if "question_text" in payload:
            return {"questions": [payload]}
    raise ValueError("LLM output must be a question object, list, or batch object")


def parse_llm_json_output(raw_output: str) -> GeneratedQuestionBatch:
    text = _strip_json_code_fence(raw_output)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON output: {exc}") from exc

    normalized_payload = _normalize_json_payload(payload)
    return GeneratedQuestionBatch.model_validate(normalized_payload)


__all__ = [
    "GeneratedOption",
    "GeneratedQuestion",
    "GeneratedQuestionBatch",
    "parse_llm_json_output",
]
