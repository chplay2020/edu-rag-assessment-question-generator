from app.ai.validation.bloom_classifier import (
    classify_bloom_level,
    classify_difficulty,
    normalize_bloom_level,
    normalize_difficulty,
)


def test_normalize_bloom_level():
    assert normalize_bloom_level(" Analyze ") == "analyze"
    assert normalize_bloom_level("memorize") is None


def test_classify_bloom_level_remember():
    assert classify_bloom_level("Hệ điều hành là gì?") == "remember"


def test_classify_bloom_level_analyze():
    assert classify_bloom_level("Phân tích vai trò của bộ nhớ ảo") == "analyze"


def test_classify_bloom_level_default_understand():
    assert classify_bloom_level("Trình bày ý nghĩa của quản lý tiến trình") == "understand"


def test_normalize_difficulty():
    assert normalize_difficulty(" Hard ") == "hard"
    assert normalize_difficulty("advanced") is None


def test_classify_difficulty_from_bloom_level():
    assert classify_difficulty("Thiết kế thuật toán", "create") == "hard"
    assert classify_difficulty("Áp dụng khái niệm", "apply") == "medium"
    assert classify_difficulty("Định nghĩa thuật ngữ", "remember") == "easy"
