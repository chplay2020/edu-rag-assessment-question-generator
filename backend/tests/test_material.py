import io
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services import material_service


class FakeDB:
    def __init__(self):
        self.added = None

    def add(self, obj):
        self.added = obj

    def commit(self):
        pass

    def refresh(self, obj):
        obj.id = 1

    def rollback(self):
        pass


def _upload_file(filename: str, content_type: str):
    return SimpleNamespace(
        filename=filename,
        content_type=content_type,
        file=io.BytesIO(b"contract test content"),
    )


def test_upload_material_creates_uploaded_status(tmp_path, monkeypatch):
    monkeypatch.setattr(material_service, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(material_service.course_service, "get_course", lambda **kwargs: object())

    material = material_service.upload_material(
        db=FakeDB(),
        course_id=1,
        file=_upload_file("lesson.txt", "text/plain"),
        current_user_id=7,
        current_user_role="lecturer",
    )

    assert material.status == "uploaded"


def test_docx_upload_is_rejected_until_extraction_is_supported(monkeypatch):
    monkeypatch.setattr(material_service.course_service, "get_course", lambda **kwargs: object())

    with pytest.raises(HTTPException) as exc_info:
        material_service.upload_material(
            db=FakeDB(),
            course_id=1,
            file=_upload_file(
                "lesson.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            current_user_id=7,
            current_user_role="lecturer",
        )

    assert exc_info.value.status_code == 400
    assert "PDF hoặc TXT" in exc_info.value.detail
