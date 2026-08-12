from app.ai.extraction.pdf_extractor import extract_and_save_raw_text, extract_text_from_file


def test_extraction_adapter_extracts_txt_and_saves_raw(tmp_path, monkeypatch):
    source = tmp_path / "lesson.txt"
    source.write_text("Raw lesson text", encoding="utf-8")
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))

    assert extract_text_from_file(source) == "Raw lesson text"

    raw_text, raw_path = extract_and_save_raw_text(123, source)

    assert raw_text == "Raw lesson text"
    assert raw_path.endswith("material_123/raw.txt")
    assert (tmp_path / "processed" / "material_123" / "raw.txt").read_text(
        encoding="utf-8"
    ) == "Raw lesson text"
