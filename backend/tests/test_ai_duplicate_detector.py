from types import SimpleNamespace

from app.ai.validation import duplicate_detector


def test_duplicate_detector_returns_duplicate_when_score_above_threshold(monkeypatch):
    class FakeVectorStore:
        def search_material_chunks(self, **kwargs):
            return [SimpleNamespace(score=0.95, payload={"chunk_id": 1})]

    monkeypatch.setattr(duplicate_detector, "embed_query", lambda text: [0.1, 0.2])
    monkeypatch.setattr(duplicate_detector, "get_vector_store", lambda: FakeVectorStore())

    result = duplicate_detector.detect_duplicate_question(
        "Hệ điều hành là gì?",
        material_id=1,
        course_id=2,
        threshold=0.9,
    )

    assert result.is_duplicate is True
    assert len(result.matches) == 1
    assert result.warnings == []


def test_duplicate_detector_returns_not_duplicate_when_below_threshold(monkeypatch):
    class FakeVectorStore:
        def search_material_chunks(self, **kwargs):
            return [{"score": 0.5, "payload": {"chunk_id": 1}}]

    monkeypatch.setattr(duplicate_detector, "embed_query", lambda text: [0.1, 0.2])
    monkeypatch.setattr(duplicate_detector, "get_vector_store", lambda: FakeVectorStore())

    result = duplicate_detector.detect_duplicate_question("Câu hỏi mới", threshold=0.9)

    assert result.is_duplicate is False
    assert len(result.matches) == 1


def test_duplicate_detector_does_not_crash_when_qdrant_unavailable(monkeypatch):
    class FailingVectorStore:
        def search_material_chunks(self, **kwargs):
            raise RuntimeError("qdrant unavailable")

    monkeypatch.setattr(duplicate_detector, "embed_query", lambda text: [0.1, 0.2])
    monkeypatch.setattr(duplicate_detector, "get_vector_store", lambda: FailingVectorStore())

    result = duplicate_detector.detect_duplicate_question("Hệ điều hành là gì?")

    assert result.is_duplicate is False
    assert result.matches == []
    assert result.warnings
    assert "qdrant unavailable" in result.warnings[0]


def test_duplicate_detector_skips_empty_question():
    result = duplicate_detector.detect_duplicate_question("   ")

    assert result.is_duplicate is False
    assert result.matches == []
    assert "question_text is empty" in result.warnings[0]
