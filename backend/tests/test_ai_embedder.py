from app.ai.embedding.embedder import FakeDeterministicEmbedder


def test_fake_embedding_is_deterministic():
    embedder = FakeDeterministicEmbedder(dimension=8, model_name="test-model")

    first = embedder.embed_texts(["same text"])[0]
    second = embedder.embed_texts(["same text"])[0]
    different = embedder.embed_texts(["different text"])[0]

    assert first == second
    assert first != different
    assert len(first) == 8


def test_fake_embed_query_matches_text_embedding_for_same_input():
    embedder = FakeDeterministicEmbedder(dimension=8, model_name="test-model")

    assert embedder.embed_query("search text") == embedder.embed_texts(["search text"])[0]
