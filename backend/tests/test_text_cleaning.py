import os
import pytest
from app.services.text_cleaning_service import clean_text, clean_and_save

def test_clean_text_whitespace_and_newlines():
    raw_text = "  Dòng   chứa    nhiều khoảng   trắng.  \n\n\n\n  Dòng tiếp theo.  \r\n\r\nCuối cùng."
    expected = "Dòng chứa nhiều khoảng trắng.\n\nDòng tiếp theo.\n\nCuối cùng."
    assert clean_text(raw_text) == expected

def test_clean_text_form_feed_removal():
    raw_text = "Trang 1\n\f\nTrang 2"
    expected = "Trang 1\n\nTrang 2"
    assert clean_text(raw_text) == expected

def test_clean_text_repeated_header_removal():
    raw_text = """Bài giảng Hệ Điều Hành
Nội dung trang 1.
Chương 1: Giới thiệu.
Trang 1
\f
Bài giảng Hệ Điều Hành
Nội dung trang 2.
Trang 2
\f
Bài giảng Hệ Điều Hành
Nội dung trang 3.
Đây là một heading bình thường không lặp.
Trang 3
"""
    expected = "Nội dung trang 1.\nChương 1: Giới thiệu.\nTrang 1\n\nNội dung trang 2.\nTrang 2\n\nNội dung trang 3.\nĐây là một heading bình thường không lặp.\nTrang 3"
    assert clean_text(raw_text) == expected

def test_clean_text_repeated_header_footer_removal():
    raw_text_with_footer = """Bài giảng HĐH
Nội dung 1
Footer môn học
\f
Bài giảng HĐH
Nội dung 2
Footer môn học
\f
Bài giảng HĐH
Nội dung 3
Footer môn học
"""
    expected = "Nội dung 1\n\nNội dung 2\n\nNội dung 3"
    assert clean_text(raw_text_with_footer) == expected

def test_clean_text_isolated_page_numbers():
    raw_text = """Chương 1: Mở đầu
Nội dung trang 1.
1
\f
2
Nội dung trang 2.
Năm xuất bản 2026.
\f
Nội dung trang 3.
18/03/2026
3
"""
    # 1, 2, 3 đứng riêng ở đầu/cuối sẽ bị xóa
    # "Chương 1: Mở đầu", "2026" bên trong (hoặc > 999), "18/03/2026" sẽ được giữ
    expected = "Chương 1: Mở đầu\nNội dung trang 1.\n\nNội dung trang 2.\nNăm xuất bản 2026.\n\nNội dung trang 3.\n18/03/2026"
    assert clean_text(raw_text) == expected

def test_clean_text_keep_non_repetitive_content():
    raw_text = """Header chung
Chương 1: Mở đầu
Đoạn văn quan trọng.
\f
Header chung
Chương 2: Nội dung
Đoạn văn khác.
"""
    # Đầu ra không được xóa "Chương 1", "Chương 2" vì chúng không lặp
    expected = "Chương 1: Mở đầu\nĐoạn văn quan trọng.\n\nChương 2: Nội dung\nĐoạn văn khác."
    assert clean_text(raw_text) == expected

def test_clean_and_save(tmp_path, monkeypatch):
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path))
    
    material_id = 999
    raw_text = "   Văn bản   cần làm   sạch.  \n\n\n"
    
    saved_path = clean_and_save(material_id, raw_text)
    
    expected_path = os.path.join(str(tmp_path), f"material_{material_id}", "clean.txt").replace("\\", "/")
    assert saved_path == expected_path
    
    assert os.path.exists(saved_path)
    with open(saved_path, "r", encoding="utf-8") as f:
        assert f.read() == "Văn bản cần làm sạch."
