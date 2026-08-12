from types import SimpleNamespace

from app.ai.generation import question_generator
from app.ai.generation.output_parser import GeneratedQuestionBatch


def _context_chunks():
    return [
        SimpleNamespace(
            chunk_id=101,
            material_id=1,
            course_id=2,
            content="Virtual memory is a memory management technique.",
            score=0.95,
            payload={"chunk_id": 101},
        )
    ]


def test_fake_provider_generates_requested_number_of_questions(monkeypatch):
    monkeypatch.setattr(question_generator.settings, "LLM_PROVIDER", "fake")
    monkeypatch.setattr(question_generator.settings, "GEMINI_API_KEY", None)

    batch = question_generator.generate_questions(
        context_chunks=_context_chunks(),
        material_id=1,
        course_id=2,
        number_of_questions=3,
        difficulty="medium",
        bloom_level="understand",
    )

    assert isinstance(batch, GeneratedQuestionBatch)
    assert len(batch.questions) == 3
    for question in batch.questions:
        assert len(question.options) == 4
        assert sum(option.is_correct for option in question.options) == 1
        assert question.correct_answer in [option.text for option in question.options]
        assert question.source_chunk_ids == [101]


def test_question_generator_output_parses_successfully(monkeypatch):
    monkeypatch.setattr(question_generator.settings, "LLM_PROVIDER", "fake")
    monkeypatch.setattr(question_generator.settings, "GEMINI_API_KEY", None)

    batch = question_generator.generate_questions(
        context_chunks=_context_chunks(),
        material_id=1,
        course_id=2,
        number_of_questions=1,
        difficulty="hard",
        bloom_level="analyze",
        language="vi",
    )

    question = batch.questions[0]
    assert question.difficulty == "hard"
    assert question.bloom_level == "analyze"


def test_fake_provider_does_not_call_gemini(monkeypatch):
    monkeypatch.setattr(question_generator.settings, "LLM_PROVIDER", "fake")
    monkeypatch.setattr(question_generator.settings, "GEMINI_API_KEY", "fake-key")

    def fail_if_called(self, prompt):
        raise AssertionError("Gemini provider must not be called in fake mode")

    monkeypatch.setattr(
        question_generator.GeminiLLMProvider,
        "generate_text",
        fail_if_called,
    )

    batch = question_generator.generate_questions(
        context_chunks=_context_chunks(),
        material_id=1,
        course_id=2,
        number_of_questions=2,
    )

    assert len(batch.questions) == 2


def test_gemini_without_api_key_falls_back_to_fake(monkeypatch):
    monkeypatch.setattr(question_generator.settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(question_generator.settings, "GEMINI_API_KEY", None)

    provider = question_generator.get_llm_provider(
        number_of_questions=1,
        difficulty="medium",
        bloom_level=None,
        source_chunk_ids=[101],
        language="vi",
    )

    assert isinstance(provider, question_generator.FakeLLMProvider)

    batch = question_generator.generate_questions(
        context_chunks=_context_chunks(),
        material_id=1,
        course_id=2,
        number_of_questions=1,
    )
    assert len(batch.questions) == 1


def test_build_mcq_prompt_includes_context_and_requirements(monkeypatch):
    monkeypatch.setattr(question_generator.settings, "LLM_PROVIDER", "fake")

    prompt = question_generator.build_mcq_prompt(
        context_chunks=_context_chunks(),
        number_of_questions=2,
        difficulty="easy",
        bloom_level="remember",
        language="vi",
    )

    assert "Virtual memory is a memory management technique." in prompt
    assert "number_of_questions: 2" in prompt
    assert "difficulty: easy" in prompt
    assert "bloom_level: remember" in prompt
    assert "language: vi" in prompt
