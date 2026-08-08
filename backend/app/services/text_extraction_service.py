import os
from pathlib import Path
import fitz  # PyMuPDF
from app.models.material import Material

class TextExtractionError(Exception):
    pass

# hàm trích xuất text từ file pdf
def extract_pdf_text(file_path: str | Path) -> str:
    if not os.path.exists(file_path):
        raise TextExtractionError(f"File not found: {file_path}")
    
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise TextExtractionError(f"Failed to open PDF: {e}")
    
    pages_text = []
    for page in doc:
        text = page.get_text()
        pages_text.append(text)
    
    doc.close()
    
    if not pages_text:
        raise TextExtractionError("PDF is empty.")
    
    # Kiểm tra văn bản có được trích xuất hay không (dùng để xử lý PDF scan không có OCR)
    full_text = "".join(pages_text).strip()
    if not full_text:
        raise TextExtractionError("No extractable text found in PDF (possibly scanned).")
        
    return "\n\f\n".join(pages_text)

# hàm trích xuất text từ file txt với các encoding khác nhau
def extract_txt_text(file_path: str | Path) -> str:
    if not os.path.exists(file_path):
        raise TextExtractionError(f"File not found: {file_path}")
    
    encodings = ["utf-8-sig", "utf-8", "cp1258"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise TextExtractionError(f"Failed to decode TXT file: {file_path} with supported encodings.")

# hàm trích xuất text từ file với các encoding khác nhau
def extract_text(file_path: str | Path) -> str:
    if not os.path.exists(file_path):
        raise TextExtractionError(f"File not found: {file_path}")
        
    path_str = str(file_path).lower()
    if path_str.endswith(".pdf"):
        return extract_pdf_text(file_path)
    elif path_str.endswith(".txt"):
        return extract_txt_text(file_path)
    else:
        raise TextExtractionError(f"Unsupported file format: {file_path}")

# hàm lưu raw text vào file
def save_raw_text(material_id: int, text: str) -> str:
    processed_dir = os.environ.get("PROCESSED_DIR", "storage/processed")
    target_dir = os.path.join(processed_dir, f"material_{material_id}")
    os.makedirs(target_dir, exist_ok=True)
    
    target_path = os.path.join(target_dir, "raw.txt")
    temp_path = target_path + ".tmp"
    
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(text)
        
    os.replace(temp_path, target_path)
    
    # Trả về đường dẫn dạng chuỗi với /
    return target_path.replace("\\", "/")

# hàm kết hợp trích xuất và lưu raw text
def extract_and_save(material: Material) -> str:
    text = extract_text(material.file_path)
    raw_txt_path = save_raw_text(material.id, text)
    return raw_txt_path
