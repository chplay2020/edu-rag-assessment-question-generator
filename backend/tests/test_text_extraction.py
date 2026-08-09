import os
import pytest
import fitz
from pathlib import Path
from app.services.text_extraction_service import (
    TextExtractionError,
    extract_txt_text,
    extract_pdf_text,
    extract_text,
    save_raw_text,
    extract_and_save
)
from app.models.material import Material

# Test trích xuất text từ file txt với encoding utf-8 tiếng việt
def test_extract_txt_utf8_vietnamese(tmp_path):
    file_path = tmp_path / "test_vi.txt"
    content = "Xin chào Việt Nam"
    file_path.write_text(content, encoding="utf-8")
    assert extract_txt_text(file_path) == content

# Từ file txt với encoding utf-8-sig (BOM)
def test_extract_txt_utf8_bom(tmp_path):
    file_path = tmp_path / "test_bom.txt"
    content = "Hello with BOM"
    file_path.write_text(content, encoding="utf-8-sig")
    assert extract_txt_text(file_path) == content

# Test trích xuất text từ file pdf
def test_extract_pdf_text_based(tmp_path):
    file_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello PDF")
    doc.save(file_path)
    doc.close()
    
    text = extract_pdf_text(file_path)
    assert "Hello PDF" in text

# Từ file pdf nhiều trang và phân tách trang
def test_extract_pdf_multipage_separator(tmp_path):
    file_path = tmp_path / "multi.pdf"
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Page 1")
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Page 2")
    doc.save(file_path)
    doc.close()
    
    text = extract_pdf_text(file_path)
    assert "\n\f\n" in text
    assert "Page 1" in text
    assert "Page 2" in text

# Khi file pdf không có text
def test_extract_pdf_empty_throws_error(tmp_path):
    file_path = tmp_path / "empty.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(file_path)
    doc.close()
    
    with pytest.raises(TextExtractionError, match="No extractable text"):
        extract_pdf_text(file_path)

# Khi file không tồn tại
def test_extract_file_not_found():
    with pytest.raises(TextExtractionError, match="File not found"):
        extract_text("nonexistent.txt")

# Khi file có định dạng không được hỗ trợ
def test_extract_unsupported_extensions(tmp_path):
    docx_file = tmp_path / "test.docx"
    docx_file.write_text("dummy")
    mp4_file = tmp_path / "test.mp4"
    mp4_file.write_text("dummy")
    
    with pytest.raises(TextExtractionError, match="Unsupported file format"):
        extract_text(docx_file)
        
    with pytest.raises(TextExtractionError, match="Unsupported file format"):
        extract_text(mp4_file)

# Test lưu raw text vào file
def test_save_raw_text(tmp_path, monkeypatch):
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path))
    
    material_id = 123
    text = "Extracted text content"
    
    saved_path = save_raw_text(material_id, text)
    
    expected_path = os.path.join(str(tmp_path), f"material_{material_id}", "raw.txt").replace("\\", "/")
    assert saved_path == expected_path
    assert os.path.exists(saved_path)
    with open(saved_path, "r", encoding="utf-8") as f:
        assert f.read() == text

# Hàm kết hợp trích xuất và lưu raw text, đảm bảo không làm thay đổi file gốc
def test_extract_and_save_no_modification_to_original(tmp_path, monkeypatch):
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))
    
    source_file = tmp_path / "source.txt"
    source_content = "Original Content"
    source_file.write_text(source_content, encoding="utf-8")
    
    m = Material(id=999, file_path=str(source_file))
    
    saved_path = extract_and_save(m)
    
    assert os.path.exists(source_file)
    assert source_file.read_text(encoding="utf-8") == source_content
    
    assert os.path.exists(saved_path)
    with open(saved_path, "r", encoding="utf-8") as f:
        assert f.read() == source_content
