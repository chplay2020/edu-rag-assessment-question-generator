import os
import re

def clean_text(raw_text: str) -> str:

    # Chuẩn hóa xuống dòng
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Chia theo trang bằng form-feed \f
    pages = text.split("\f")
    
    cleaned_pages = []
    for page in pages:
        lines = page.split("\n")
        cleaned_lines = []
        for line in lines:
            # Cắt khoảng trắng thừa
            line = line.strip() 
            # Gộp nhiều khoảng trắng thành 1
            line = re.sub(r'[ \t]+', ' ', line)
            cleaned_lines.append(line)
        cleaned_pages.append(cleaned_lines)
        
    # Xử lý loại bỏ Header / Footer lặp lại (nếu có từ 2 trang trở lên)
    if len(cleaned_pages) >= 2:
        first_lines = {}
        last_lines = {}
        
        # Tìm dòng đầu/cuối có chứa nội dung của từng trang
        for i, page_lines in enumerate(cleaned_pages):
            non_empty = [l for l in page_lines if l]
            if non_empty:
                first_lines[i] = non_empty[0]
                last_lines[i] = non_empty[-1]
                
        # Đếm số lần xuất hiện
        first_line_counts = {}
        for line in first_lines.values():
            first_line_counts[line] = first_line_counts.get(line, 0) + 1
            
        last_line_counts = {}
        for line in last_lines.values():
            last_line_counts[line] = last_line_counts.get(line, 0) + 1
            
        # Xác định header/footer (lặp lại >= 2 lần và độ dài < 100 ký tự)
        headers_to_remove = {line for line, count in first_line_counts.items() if count >= 2 and len(line) < 100}
        footers_to_remove = {line for line, count in last_line_counts.items() if count >= 2 and len(line) < 100}
        
        # Xóa các dòng được cho là header/footer
        for i, page_lines in enumerate(cleaned_pages):
            non_empty_indices = [idx for idx, l in enumerate(page_lines) if l]
            if non_empty_indices:
                first_idx = non_empty_indices[0]
                last_idx = non_empty_indices[-1]
                
                # Nếu trang này có dòng đầu thuộc nhóm header cần xóa
                if page_lines[first_idx] in headers_to_remove:
                    page_lines[first_idx] = ""
                    
                # Nếu trang này có dòng cuối thuộc nhóm footer cần xóa (kiểm tra lại để tránh xóa nhầm nếu trang chỉ có 1 dòng)
                if page_lines[last_idx] in footers_to_remove and last_idx != first_idx:
                    page_lines[last_idx] = ""
                # Xử lý trường hợp last_idx == first_idx và nó vừa là header vừa là footer (hiếm khi xảy ra)
                elif page_lines[last_idx] in footers_to_remove and last_idx == first_idx and page_lines[last_idx] != "":
                    page_lines[last_idx] = ""

    # Xóa số trang đứng độc lập ở đầu hoặc cuối trang (trước khi gộp trang)
    for page_lines in cleaned_pages:
        non_empty_indices = [idx for idx, l in enumerate(page_lines) if l]
        if non_empty_indices:
            first_idx = non_empty_indices[0]
            # Chỉ xóa nếu là số nguyên dương <= 999 để tránh xóa năm như 2026
            if re.match(r"^[1-9]\d{0,2}$", page_lines[first_idx]):
                page_lines[first_idx] = ""
                
        # Lấy lại indices do first_idx có thể vừa bị xóa
        non_empty_indices = [idx for idx, l in enumerate(page_lines) if l]
        if non_empty_indices:
            last_idx = non_empty_indices[-1]
            if re.match(r"^[1-9]\d{0,2}$", page_lines[last_idx]):
                page_lines[last_idx] = ""

    # Gộp tất cả các trang lại, bỏ qua \f
    final_lines = []
    for page_lines in cleaned_pages:
        final_lines.extend(page_lines)
        
    # Thu gọn nhiều dòng trống liên tiếp thành tối đa 1 dòng trống
    result_lines = []
    empty_streak = 0
    for line in final_lines:
        if not line:
            empty_streak += 1
            if empty_streak <= 1:
                result_lines.append("")
        else:
            empty_streak = 0
            result_lines.append(line)
            
    return "\n".join(result_lines).strip()

# Hàm xử lý và lưu file clean.txt
def clean_and_save(material_id: int, raw_text: str) -> str:
    cleaned_text = clean_text(raw_text)
    
    processed_dir = os.environ.get("PROCESSED_DIR", "storage/processed")
    target_dir = os.path.join(processed_dir, f"material_{material_id}")
    os.makedirs(target_dir, exist_ok=True)
    
    target_path = os.path.join(target_dir, "clean.txt")
    temp_path = target_path + ".tmp"
    
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
        
    os.replace(temp_path, target_path)
    
    return target_path.replace("\\", "/")
