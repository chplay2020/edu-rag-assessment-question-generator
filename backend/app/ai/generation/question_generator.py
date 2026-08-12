import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, cast

from app.ai.generation.output_parser import (
    GeneratedQuestionBatch,
    parse_llm_json_output,
)
from app.ai.retrieval.retriever import build_context_text
from app.core.config import settings


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "generate_mcq.txt"


class LLMProviderError(Exception):
    pass


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, *, api_key: str, model_name: str) -> None:
        if not api_key:
            raise LLMProviderError("GEMINI_API_KEY is required for Gemini provider")
        self.api_key = api_key
        self.model_name = model_name

    def generate_text(self, prompt: str) -> str:
        try:
            from google import genai  # type: ignore
        except ImportError as exc:
            raise LLMProviderError(
                "google-genai is required for Gemini provider"
            ) from exc

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        text = getattr(response, "text", None)
        if not text:
            raise LLMProviderError("Gemini returned an empty response")
        return cast(str, text)


class FakeLLMProvider(BaseLLMProvider):
    def __init__(
        self,
        *,
        number_of_questions: int = 1,
        difficulty: str = "medium",
        bloom_level: str | None = None,
        source_chunk_ids: list[int] | None = None,
        language: str = "vi",
    ) -> None:
        self.number_of_questions = number_of_questions
        self.difficulty = difficulty
        self.bloom_level = bloom_level or "understand"
        self.source_chunk_ids = source_chunk_ids or [1]
        self.language = language

    def generate_text(self, prompt: str) -> str:
        questions = []
        for index in range(self.number_of_questions):
            correct_answer = f"Dap an dung {index + 1}"
            questions.append(
                {
                    "question_text": f"Cau hoi gia lap {index + 1}?",
                    "options": [
                        {"text": correct_answer, "is_correct": True},
                        {"text": f"Dap an nhieu A {index + 1}", "is_correct": False},
                        {"text": f"Dap an nhieu B {index + 1}", "is_correct": False},
                        {"text": f"Dap an nhieu C {index + 1}", "is_correct": False},
                    ],
                    "correct_answer": correct_answer,
                    "difficulty": self.difficulty,
                    "bloom_level": self.bloom_level,
                    "explanation": "Cau hoi gia lap duoc sinh tu FakeLLMProvider.",
                    "source_chunk_ids": self.source_chunk_ids,
                }
            )

        return json.dumps({"questions": questions}, ensure_ascii=False)


def _read_prompt_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _get_chunk_value(chunk: Any, key: str, default: Any = None) -> Any:
    if isinstance(chunk, dict):
        return chunk.get(key, default)
    return getattr(chunk, key, default)


def _source_chunk_ids(context_chunks: list[Any]) -> list[int]:
    ids: list[int] = []
    for chunk in context_chunks:
        raw_chunk_id = _get_chunk_value(chunk, "chunk_id")
        if raw_chunk_id is not None:
            ids.append(int(raw_chunk_id))
    return ids or [1]


def _context_text(context_chunks: list[Any]) -> str:
    try:
        return build_context_text(context_chunks)
    except AttributeError:
        parts = []
        for chunk in context_chunks:
            chunk_id = _get_chunk_value(chunk, "chunk_id", "unknown")
            material_id = _get_chunk_value(chunk, "material_id", "unknown")
            course_id = _get_chunk_value(chunk, "course_id", "unknown")
            score = _get_chunk_value(chunk, "score", 0.0)
            content = _get_chunk_value(chunk, "content", "")
            parts.append(
                f"[chunk_id={chunk_id}; material_id={material_id}; "
                f"course_id={course_id}; score={float(score):.4f}]\n{content}"
            )
        return "\n\n".join(parts)


def build_mcq_prompt(
    *,
    context_chunks: list[Any],
    number_of_questions: int,
    difficulty: str,
    bloom_level: str | None,
    language: str,
) -> str:
    prompt_template = _read_prompt_template()
    replacements = {
        "{context}": _context_text(context_chunks),
        "{number_of_questions}": str(number_of_questions),
        "{difficulty}": difficulty,
        "{bloom_level}": bloom_level or "any",
        "{language}": language,
    }
    prompt = prompt_template
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)
    return prompt


def get_llm_provider(
    *,
    number_of_questions: int,
    difficulty: str,
    bloom_level: str | None,
    source_chunk_ids: list[int],
    language: str,
) -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower().strip()
    api_key = settings.GEMINI_API_KEY

    if provider == "fake" or not api_key:
        return FakeLLMProvider(
            number_of_questions=number_of_questions,
            difficulty=difficulty,
            bloom_level=bloom_level,
            source_chunk_ids=source_chunk_ids,
            language=language,
        )

    if provider == "gemini":
        return GeminiLLMProvider(
            api_key=api_key,
            model_name=settings.LLM_MODEL,
        )

    raise LLMProviderError(f"Unsupported LLM provider '{settings.LLM_PROVIDER}'")


def generate_questions(
    context_chunks: list[Any],
    material_id: int,
    course_id: int,
    number_of_questions: int = 5,
    difficulty: str = "medium",
    bloom_level: str | None = None,
    language: str = "vi",
) -> GeneratedQuestionBatch:
    if number_of_questions <= 0:
        raise ValueError("number_of_questions must be greater than 0")

    source_chunk_ids = _source_chunk_ids(context_chunks)
    prompt = build_mcq_prompt(
        context_chunks=context_chunks,
        number_of_questions=number_of_questions,
        difficulty=difficulty,
        bloom_level=bloom_level,
        language=language,
    )
    provider = get_llm_provider(
        number_of_questions=number_of_questions,
        difficulty=difficulty,
        bloom_level=bloom_level,
        source_chunk_ids=source_chunk_ids,
        language=language,
    )
    raw_output = provider.generate_text(prompt)
    return parse_llm_json_output(raw_output)


__all__ = [
    "BaseLLMProvider",
    "FakeLLMProvider",
    "GeminiLLMProvider",
    "LLMProviderError",
    "build_mcq_prompt",
    "generate_questions",
    "get_llm_provider",
]
