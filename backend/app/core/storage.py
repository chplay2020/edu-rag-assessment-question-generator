"""Helpers for resolving backend-owned storage paths independently of cwd."""

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]


def get_processed_dir() -> Path:
    """Return the configured processed-data directory.

    Relative ``PROCESSED_DIR`` values are resolved from the backend project root,
    not from the process working directory. This keeps local and Docker runs on
    the same ``backend/storage/processed`` tree.
    """
    configured = Path(os.environ.get("PROCESSED_DIR", "storage/processed"))
    if not configured.is_absolute():
        configured = BACKEND_DIR / configured
    return configured.resolve()


def get_export_dir() -> Path:
    """Return the configured export data directory."""
    configured = Path(os.environ.get("EXPORT_DIR", "storage/exports"))
    if not configured.is_absolute():
        configured = BACKEND_DIR / configured
    return configured.resolve()


__all__ = ["get_processed_dir", "get_export_dir"]
