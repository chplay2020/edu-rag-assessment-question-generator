"""LLM judge cho câu hỏi đã sinh (T042).

Luật ở `question_validator` chỉ bắt được lỗi cấu trúc: nó không biết đáp án
"đúng" có thật sự đúng theo tài liệu hay không. Judge dùng chính Gemini để
chấm lại phần ngữ nghĩa đó.

Judge là bước tuỳ chọn (`ENABLE_LLM_JUDGE`): nó nhân đôi số lần gọi API, nên
mặc định tắt và chỉ bật khi cần chất lượng cao. Judge lỗi thì pipeline bỏ qua
kết quả judge chứ không làm hỏng job.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Sequence

from app.ai.generation.output_parser import GeneratedQuestion
from app.ai.llm.gemini_provider import GeminiLLMProvider, is_gemini_available
from app.ai.prompts import render_prompt
from app.core.config import settings


logger = logging.getLogger(__name__)

JUDGE_SYSTEM_INSTRUCTION = (
    "You are a strict assessment-quality judge. You answer only with JSON "
    "matching the requested schema and you judge only against the given context."
)

JUDGE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "verdicts": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "index": {"type": "INTEGER"},
                    "is_valid": {"type": "BOOLEAN"},
                    "errors": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "warnings": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "scores": {
                        "type": "OBJECT",
                        "properties": {
                            "grounding": {"type": "NUMBER"},
                            "clarity": {"type": "NUMBER"},
                            "distractor_quality": {"type": "NUMBER"},
                            "assessment_quality": {"type": "NUMBER"},
                        },
                    },
                },
                "required": ["index", "is_valid", "errors", "warnings", "scores"],
                "propertyOrdering": ["index", "is_valid", "errors", "warnings", "scores"],
            },
        }
    },
    "required": ["verdicts"],
}


@dataclass
class JudgeVerdict:
    index: int
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def average_score(self) -> float:
        if not self.scores:
            return 1.0
        return sum(self.scores.values()) / len(self.scores)


def is_judge_enabled() -> bool:
    return bool(settings.ENABLE_LLM_JUDGE) and is_gemini_available()


def _questions_payload(questions: Sequence[GeneratedQuestion]) -> str:
    payload = [
        {
            "index": index,
            "question_text": question.question_text,
            "options": [
                {"text": option.text, "is_correct": option.is_correct}
                for option in question.options
            ],
            "correct_answer": question.correct_answer,
            "difficulty": question.difficulty,
            "bloom_level": question.bloom_level,
            "explanation": question.explanation,
            "source_chunk_ids": question.source_chunk_ids,
        }
        for index, question in enumerate(questions)
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _parse_verdicts(raw_output: str, expected: int) -> dict[int, JudgeVerdict]:
    payload = json.loads(raw_output)
    raw_verdicts = payload.get("verdicts") if isinstance(payload, dict) else payload
    if not isinstance(raw_verdicts, list):
        raise ValueError("judge output thiếu mảng 'verdicts'")

    verdicts: dict[int, JudgeVerdict] = {}
    for position, item in enumerate(raw_verdicts):
        if not isinstance(item, dict):
            continue
        index = item.get("index", position)
        if not isinstance(index, int) or not 0 <= index < expected:
            continue
        raw_scores = item.get("scores") or {}
        scores = {
            key: float(value)
            for key, value in raw_scores.items()
            if isinstance(value, (int, float))
        }
        verdicts[index] = JudgeVerdict(
            index=index,
            is_valid=bool(item.get("is_valid", True)),
            errors=[str(error) for error in item.get("errors") or []],
            warnings=[str(warning) for warning in item.get("warnings") or []],
            scores=scores,
        )
    return verdicts


def judge_questions(
    questions: Sequence[GeneratedQuestion],
    *,
    context_text: str,
) -> dict[int, JudgeVerdict]:
    """Chấm cả lô trong một lần gọi. Trả về dict rỗng khi judge tắt hoặc lỗi."""
    if not questions or not is_judge_enabled():
        return {}

    prompt = render_prompt(
        "validate_question",
        context=context_text,
        questions=_questions_payload(questions),
    )
    provider = GeminiLLMProvider(
        system_instruction=JUDGE_SYSTEM_INSTRUCTION,
        response_schema=JUDGE_RESPONSE_SCHEMA,
        temperature=0.0,
    )

    try:
        raw_output = provider.generate_text(prompt)
        return _parse_verdicts(raw_output, len(questions))
    except Exception as exc:
        logger.warning("LLM judge thất bại, bỏ qua bước chấm: %s", exc)
        return {}


__all__ = [
    "JUDGE_RESPONSE_SCHEMA",
    "JudgeVerdict",
    "is_judge_enabled",
    "judge_questions",
]
