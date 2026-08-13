from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionError,
    extract_pdf_text,
    extract_text,
    extract_txt_text,
    save_raw_text,
)


def extract_text_from_file(file_path: str | Path) -> str:
    """Adapter trích xuất văn bản cho AI pipeline.

    Logic trích xuất cụ thể đang nằm trong text_extraction_service.
    Cách này giúp API, worker và các module AI sau này dùng chung một hành vi,
    tránh việc mỗi nơi tự viết một kiểu xử lý file khác nhau.
    """
    return extract_text(file_path)


def extract_and_save_raw_text(material_id: int, file_path: str | Path) -> tuple[str, str]:
    """Trích xuất văn bản từ file và lưu nội dung raw text xuống storage.

    Trả về:
    - raw_text: nội dung văn bản thô sau khi trích xuất
    - raw_path: đường dẫn file raw.txt đã lưu
    """
    raw_text = extract_text_from_file(file_path)
    raw_path = save_raw_text(material_id, raw_text)

    return raw_text, raw_path


__all__ = [
    "TextExtractionError",
    "extract_pdf_text",
    "extract_txt_text",
    "extract_text_from_file",
    "extract_and_save_raw_text",
]