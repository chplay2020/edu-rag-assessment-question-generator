from app.services.text_cleaning_service import clean_and_save, clean_text


def clean_extracted_text(raw_text: str) -> str:
    """Adapter làm sạch văn bản cho AI pipeline.

    Hàm này bọc lại clean_text từ text_cleaning_service để các module AI
    có thể import từ app.ai.extraction thay vì gọi trực tiếp service tầng ngoài.
    """
    return clean_text(raw_text)


def clean_and_save_text(material_id: int, raw_text: str) -> tuple[str, str]:
    """Làm sạch văn bản đã trích xuất và lưu kết quả xuống storage.

    Trả về:
    - cleaned_text: nội dung đã được làm sạch
    - clean_path: đường dẫn file clean.txt đã lưu
    """
    cleaned_text = clean_extracted_text(raw_text)
    clean_path = clean_and_save(material_id, raw_text)

    return cleaned_text, clean_path


__all__ = [
    "clean_text",
    "clean_and_save",
    "clean_extracted_text",
    "clean_and_save_text",
]