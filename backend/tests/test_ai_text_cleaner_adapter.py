from app.ai.extraction.text_cleaner import clean_and_save_text, clean_extracted_text


def test_clean_text_adapter_cleans_text(tmp_path, monkeypatch):
    raw_text = "  Dòng   có   khoảng trắng.  \n\n\nDòng sau."
    monkeypatch.setenv("PROCESSED_DIR", str(tmp_path / "processed"))

    assert clean_extracted_text(raw_text) == "Dòng có khoảng trắng.\n\nDòng sau."

    cleaned_text, clean_path = clean_and_save_text(10, raw_text)

    assert cleaned_text == "Dòng có khoảng trắng.\n\nDòng sau."
    assert clean_path.endswith("material_10/clean.txt")
    assert (tmp_path / "processed" / "material_10" / "clean.txt").read_text(
        encoding="utf-8"
    ) == cleaned_text
