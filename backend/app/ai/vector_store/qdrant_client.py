from functools import lru_cache

from qdrant_client import QdrantClient

from app.core.config import settings


@lru_cache(maxsize=4)
def _build_client(url: str, api_key: str | None, timeout: int) -> QdrantClient:
    return QdrantClient(url=url, api_key=api_key, timeout=timeout)


def get_qdrant_client() -> QdrantClient:
    """Client Qdrant dùng chung (giữ connection pool thay vì tạo mới mỗi lần gọi)."""
    return _build_client(
        settings.QDRANT_URL,
        settings.QDRANT_API_KEY or None,
        settings.QDRANT_TIMEOUT_SECONDS,
    )


def reset_qdrant_client() -> None:
    """Xoá cache client (dùng khi đổi cấu hình trong test)."""
    _build_client.cache_clear()


__all__ = ["get_qdrant_client", "reset_qdrant_client"]
