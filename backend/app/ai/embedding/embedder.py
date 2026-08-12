import hashlib
import math

from app.core.config import settings


class EmbeddingProviderError(Exception):
    pass


class FakeDeterministicEmbedder:
    def __init__(self, *, dimension: int, model_name: str) -> None:
        if dimension <= 0:
            raise ValueError("Embedding dimension must be greater than 0")
        self.dimension = dimension
        self.model_name = model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def embed_query(self, query: str) -> list[float]:
        return self._embed_one(query)

    def _embed_one(self, text: str) -> list[float]:
        seed = f"{self.model_name}:{text}".encode("utf-8")
        vector: list[float] = []

        for index in range(self.dimension):
            digest = hashlib.sha256(seed + f":{index}".encode("utf-8")).digest()
            value = int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
            vector.append((value * 2.0) - 1.0)

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector
        return [value / magnitude for value in vector]


def get_embedder() -> FakeDeterministicEmbedder:
    provider = settings.EMBEDDING_PROVIDER.lower().strip()
    if provider in {"", "fake", "deterministic", "fake_deterministic"}:
        return FakeDeterministicEmbedder(
            dimension=settings.EMBEDDING_DIMENSION,
            model_name=settings.EMBEDDING_MODEL,
        )

    raise EmbeddingProviderError(
        f"Unsupported embedding provider '{settings.EMBEDDING_PROVIDER}'."
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embedder().embed_texts(texts)


def embed_query(query: str) -> list[float]:
    return get_embedder().embed_query(query)


__all__ = [
    "EmbeddingProviderError",
    "FakeDeterministicEmbedder",
    "embed_query",
    "embed_texts",
    "get_embedder",
]
