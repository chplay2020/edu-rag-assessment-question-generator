import pytest

from app.ai.chunking.chunker import chunk_text


def test_chunk_short_text_creates_one_chunk():
    chunks = chunk_text(
        "Short learning material.",
        parent_chunk_size=100,
        parent_overlap=10,
        child_chunk_size=80,
        child_overlap=10,
    )

    assert len(chunks) == 1
    assert chunks[0].content == "Short learning material."
    assert chunks[0].chunk_index == 0
    assert chunks[0].parent_id == "parent-0"


def test_chunk_long_text_creates_multiple_chunks_with_overlap():
    text = "0123456789" * 30

    chunks = chunk_text(
        text,
        parent_chunk_size=120,
        parent_overlap=20,
        child_chunk_size=50,
        child_overlap=10,
    )

    assert len(chunks) > 1
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.content for chunk in chunks)
    assert chunks[0].content[-10:] == chunks[1].content[:10]


def test_chunker_rejects_overlap_greater_than_size():
    with pytest.raises(ValueError):
        chunk_text("text", child_chunk_size=10, child_overlap=10)
