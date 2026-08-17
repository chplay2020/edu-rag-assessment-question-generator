"""Provider giả lập dùng cho unit test và môi trường không có GEMINI_API_KEY.

Sinh JSON đúng schema của `generate_mcq.txt` nên toàn bộ pipeline phía sau
(parse -> validate -> dedupe -> lưu DB) chạy y hệt luồng thật.
"""

import json

from app.ai.llm.base import BaseLLMProvider


class FakeLLMProvider(BaseLLMProvider):
    name = "fake"

    def __init__(
        self,
        *,
        number_of_questions: int = 1,
        difficulty: str = "medium",
        bloom_level: str | None = None,
        source_chunk_ids: list[int] | None = None,
        language: str = "vi",
        seed: int = 0,
    ) -> None:
        self.number_of_questions = number_of_questions
        self.difficulty = difficulty
        self.bloom_level = bloom_level or "understand"
        self.source_chunk_ids = source_chunk_ids or [1]
        self.language = language
        self.seed = seed

    def generate_text(self, prompt: str) -> str:
        questions = []
        for index in range(self.number_of_questions):
            number = self.seed + index + 1
            correct_answer = f"Dap an dung {number}"
            questions.append(
                {
                    "question_text": f"Cau hoi gia lap {number}?",
                    "options": [
                        {"text": correct_answer, "is_correct": True},
                        {"text": f"Dap an nhieu A {number}", "is_correct": False},
                        {"text": f"Dap an nhieu B {number}", "is_correct": False},
                        {"text": f"Dap an nhieu C {number}", "is_correct": False},
                    ],
                    "correct_answer": correct_answer,
                    "difficulty": self.difficulty,
                    "bloom_level": self.bloom_level,
                    "explanation": "Cau hoi gia lap duoc sinh tu FakeLLMProvider.",
                    "source_chunk_ids": self.source_chunk_ids,
                }
            )

        return json.dumps({"questions": questions}, ensure_ascii=False)


__all__ = ["FakeLLMProvider"]
