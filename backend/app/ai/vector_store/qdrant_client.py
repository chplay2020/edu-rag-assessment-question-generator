from qdrant_client import QdrantClient

from app.core.config import settings


def get_qdrant_client() -> QdrantClient:
    api_key = settings.QDRANT_API_KEY or None
    return QdrantClient(url=settings.QDRANT_URL, api_key=api_key)


__all__ = ["get_qdrant_client"]
