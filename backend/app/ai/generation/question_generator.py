"""Sinh câu hỏi MCQ từ context đã retrieve.

Cải tiến chính so với bản MVP:

- Gemini chạy ở JSON mode kèm response schema -> output đúng cấu trúc ngay.
- Parse "cứu vãn" theo từng câu: một câu hỏng không làm mất cả batch.
- Vòng lặp sinh bù: nếu model trả thiếu so với số câu yêu cầu, gọi tiếp và
  kèm danh sách câu đã có để model không lặp lại ý cũ.
- Chặn trùng ngay trong batch bằng so khớp text đã chuẩn hoá.
"""

import logging
import re
import unicodedata
from typing import Any

from app.ai.generation.output_parser import (
    MCQ_RESPONSE_SCHEMA,
    GeneratedQuestion,
    GeneratedQuestionBatch,
    parse_llm_json_output,
    parse_questions_lenient,
)
from app.ai.llm.base import BaseLLMProvider, LLMProviderError
from app.ai.llm.fake_provider import FakeLLMProvider
from app.ai.llm.gemini_provider import GeminiLLMProvider
from app.ai.prompts import prompt_version, render_prompt
from app.ai.retrieval.retriever import build_context_text
from app.core.config import settings


logger = logging.getLogger(__name__)

PROMPT_NAME = "generate_mcq"
SYSTEM_INSTRUCTION = (
    "You are an assessment question generation engine for university courses. "
    "You answer only with JSON matching the requested schema, and you never use "
    "knowledge outside the provided context."
)


def _normalize_question_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"[^\w\s]", " ", normalized).strip()


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
    return build_context_text(context_chunks)


def build_mcq_prompt(
    *,
    context_chunks: list[Any],
    number_of_questions: int,
    difficulty: str,
    bloom_level: str | None,
    language: str,
    avoid_questions: list[str] | None = None,
    allowed_chunk_ids: list[int] | None = None,
) -> str:
    chunk_ids = allowed_chunk_ids or _source_chunk_ids(context_chunks)
    avoid_text = (
        "\n".join(f"- {text}" for text in avoid_questions)
        if avoid_questions
        else "(none)"
    )
    return render_prompt(
        PROMPT_NAME,
        context=_context_text(context_chunks),
        number_of_questions=number_of_questions,
        difficulty=difficulty,
        bloom_level=bloom_level or "any",
        language=language,
        chunk_ids=", ".join(str(chunk_id) for chunk_id in chunk_ids),
        avoid_questions=avoid_text,
    )


def get_llm_provider(
    *,
    number_of_questions: int,
    difficulty: str,
    bloom_level: str | None,
    source_chunk_ids: list[int],
    language: str,
    seed: int = 0,
) -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower().strip()
    api_key = (settings.GEMINI_API_KEY or "").strip()

    if provider == "fake":
        return FakeLLMProvider(
            number_of_questions=number_of_questions,
            difficulty=difficulty,
            bloom_level=bloom_level,
            source_chunk_ids=source_chunk_ids,
            language=language,
            seed=seed,
        )

    if provider == "gemini":
        if not api_key:
            if not settings.LLM_ALLOW_FAKE_FALLBACK:
                raise LLMProviderError(
                    "LLM_PROVIDER=gemini nhưng thiếu GEMINI_API_KEY, và "
                    "LLM_ALLOW_FAKE_FALLBACK đang tắt."
                )
            logger.warning(
                "Thiếu GEMINI_API_KEY: dùng FakeLLMProvider, câu hỏi sinh ra chỉ là dữ liệu giả lập."
            )
            return FakeLLMProvider(
                number_of_questions=number_of_questions,
                difficulty=difficulty,
                bloom_level=bloom_level,
                source_chunk_ids=source_chunk_ids,
                language=language,
                seed=seed,
            )
        return GeminiLLMProvider(
            api_key=api_key,
            model_name=settings.LLM_MODEL,
            system_instruction=SYSTEM_INSTRUCTION,
            response_schema=MCQ_RESPONSE_SCHEMA,
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

    allowed_chunk_ids = _source_chunk_ids(context_chunks)
    max_attempts = max(settings.GENERATION_MAX_ATTEMPTS, 1)

    collected: list[GeneratedQuestion] = []
    seen_texts: set[str] = set()
    parse_errors: list[str] = []

    for attempt in range(1, max_attempts + 1):
        remaining = number_of_questions - len(collected)
        if remaining <= 0:
            break

        prompt = build_mcq_prompt(
            context_chunks=context_chunks,
            number_of_questions=remaining,
            difficulty=difficulty,
            bloom_level=bloom_level,
            language=language,
            avoid_questions=[question.question_text for question in collected],
            allowed_chunk_ids=allowed_chunk_ids,
        )
        provider = get_llm_provider(
            number_of_questions=remaining,
            difficulty=difficulty,
            bloom_level=bloom_level,
            source_chunk_ids=allowed_chunk_ids,
            language=language,
            seed=len(collected),
        )

        raw_output = provider.generate_text(prompt)
        questions, errors = parse_questions_lenient(raw_output)
        parse_errors.extend(errors)

        added = 0
        for question in questions:
            key = _normalize_question_text(question.question_text)
            if not key or key in seen_texts:
                continue
            seen_texts.add(key)
            collected.append(question)
            added += 1
            if len(collected) >= number_of_questions:
                break

        logger.info(
            "Sinh câu hỏi: material_id=%s attempt=%s provider=%s prompt=%s/%s "
            "yêu cầu=%s nhận=%s hợp lệ_mới=%s tổng=%s lỗi_parse=%s",
            material_id,
            attempt,
            getattr(provider, "name", type(provider).__name__),
            PROMPT_NAME,
            prompt_version(PROMPT_NAME),
            remaining,
            len(questions),
            added,
            len(collected),
            len(errors),
        )

        if added == 0 and attempt >= 2:
            # Hai lượt liên tiếp không thêm được câu nào: dừng để khỏi đốt quota.
            break

    if not collected:
        detail = "; ".join(parse_errors[:3]) if parse_errors else "model trả về batch rỗng"
        raise LLMProviderError(
            f"Không sinh được câu hỏi hợp lệ nào sau {max_attempts} lượt "
            f"(material_id={material_id}, course_id={course_id}): {detail}"
        )

    if len(collected) < number_of_questions:
        logger.warning(
            "Chỉ sinh được %s/%s câu hỏi cho material_id=%s.",
            len(collected),
            number_of_questions,
            material_id,
        )

    return GeneratedQuestionBatch(questions=collected[:number_of_questions])


__all__ = [
    "BaseLLMProvider",
    "FakeLLMProvider",
    "GeminiLLMProvider",
    "LLMProviderError",
    "build_mcq_prompt",
    "generate_questions",
    "get_llm_provider",
    "parse_llm_json_output",
]
