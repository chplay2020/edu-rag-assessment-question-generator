"""Embedding cho RAG.

Hai provider:

- `gemini`: gọi Gemini Embedding API thật. Đây là provider nên dùng khi chạy
  demo/production vì retrieval chỉ có ý nghĩa khi vector mang ngữ nghĩa thật.
  Dùng `task_type` khác nhau cho tài liệu và câu truy vấn - đây là điểm giúp
  điểm similarity tăng rõ rệt so với việc embed cả hai theo cùng một cách.
- `fake`: vector băm SHA-256, xác định và không cần mạng. Dùng cho unit test
  và môi trường offline. Lưu ý: điểm similarity của provider này vô nghĩa,
  nên retrieval sẽ rơi về cơ chế fallback trong `app.ai.retrieval`.
"""

import hashlib
import logging
import math
import random
import time
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings


logger = logging.getLogger(__name__)

# Gemini Embedding API giới hạn số lượng văn bản mỗi request.
MAX_BATCH_SIZE = 100


class EmbeddingProviderError(Exception):
    pass


class BaseEmbedder(ABC):
    dimension: int
    model_name: str

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed tài liệu (chunk) để lưu vào vector store."""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Embed câu truy vấn để tìm kiếm."""
        raise NotImplementedError


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector
    return [value / magnitude for value in vector]


class FakeDeterministicEmbedder(BaseEmbedder):
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

        return _normalize(vector)


class GeminiEmbedder(BaseEmbedder):
    def __init__(
        self,
        *,
        dimension: int | None = None,
        model_name: str | None = None,
        batch_size: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.model_name = model_name or settings.GEMINI_EMBEDDING_MODEL
        self.batch_size = min(batch_size or settings.EMBEDDING_BATCH_SIZE, MAX_BATCH_SIZE)
        self.max_retries = max_retries or settings.LLM_MAX_RETRIES

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            vectors.extend(self._embed_batch(batch, task_type="RETRIEVAL_DOCUMENT"))
        return vectors

    def embed_query(self, query: str) -> list[float]:
        return self._embed_batch([query], task_type="RETRIEVAL_QUERY")[0]

    def _embed_batch(self, texts: list[str], *, task_type: str) -> list[list[float]]:
        from app.ai.llm.gemini_provider import _is_retryable, get_gemini_client

        client = get_gemini_client()
        from google.genai import types  # type: ignore

        config = types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=self.dimension,
        )

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response: Any = client.models.embed_content(
                    model=self.model_name,
                    contents=texts,
                    config=config,
                )
            except Exception as exc:
                last_error = exc
                if not _is_retryable(exc) or attempt == self.max_retries:
                    raise EmbeddingProviderError(
                        f"Gemini embedding failed ({self.model_name}): {exc}"
                    ) from exc
                delay = settings.LLM_RETRY_BASE_DELAY * (2 ** (attempt - 1))
                delay += random.uniform(0, delay * 0.25)
                logger.warning(
                    "Gemini embedding lỗi tạm thời (attempt %s/%s), thử lại sau %.1fs: %s",
                    attempt,
                    self.max_retries,
                    delay,
                    exc,
                )
                time.sleep(delay)
                continue

            embeddings = getattr(response, "embeddings", None) or []
            if len(embeddings) != len(texts):
                raise EmbeddingProviderError(
                    f"Gemini trả về {len(embeddings)} vector cho {len(texts)} văn bản."
                )
            # Google khuyến nghị normalize khi output_dimensionality khác 3072.
            return [_normalize([float(v) for v in embedding.values]) for embedding in embeddings]

        raise EmbeddingProviderError(f"Gemini embedding failed: {last_error}")


def get_embedder() -> BaseEmbedder:
    provider = settings.EMBEDDING_PROVIDER.lower().strip()

    if provider in {"gemini", "google", "google-genai"}:
        if not (settings.GEMINI_API_KEY or "").strip():
            raise EmbeddingProviderError(
                "EMBEDDING_PROVIDER=gemini nhưng thiếu GEMINI_API_KEY."
            )
        return GeminiEmbedder()

    if provider in {"", "fake", "deterministic", "fake_deterministic"}:
        return FakeDeterministicEmbedder(
            dimension=settings.EMBEDDING_DIMENSION,
            model_name=settings.EMBEDDING_MODEL,
        )

    raise EmbeddingProviderError(
        f"Unsupported embedding provider '{settings.EMBEDDING_PROVIDER}'."
    )


def is_semantic_embedding_enabled() -> bool:
    """False khi đang dùng embedding giả -> điểm similarity không đáng tin."""
    return settings.EMBEDDING_PROVIDER.lower().strip() in {
        "gemini",
        "google",
        "google-genai",
    }


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embedder().embed_texts(texts)


def embed_query(query: str) -> list[float]:
    return get_embedder().embed_query(query)


__all__ = [
    "BaseEmbedder",
    "EmbeddingProviderError",
    "FakeDeterministicEmbedder",
    "GeminiEmbedder",
    "embed_query",
    "embed_texts",
    "get_embedder",
    "is_semantic_embedding_enabled",
]
