import io
from typing import List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from app.models.question import Question

def _sanitize_for_excel(text: str) -> str:
    """Ngăn chặn Excel Formula Injection"""
    if not text:
        return ""
    text = str(text)
    if text.startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text

def generate_excel_workbook(questions: List[Question]) -> io.BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Câu hỏi"

    # Tính số cột option tối đa (ít nhất là 4 để giữ form A, B, C, D)
    max_opts = 4
    if questions:
        max_opts = max(max([len(q.options) for q in questions] + [4]), 4)

    # 1. Tạo Header
    headers = ["STT", "Nội dung câu hỏi"]
    
    # Cột đáp án 
    for i in range(max_opts):
        letter = chr(65 + i) # A, B, C...
        headers.append(f"Đáp án {letter}")
        
    headers.extend([
        "Đáp án đúng", 
        "Giải thích", 
        "Độ khó", 
        "Bloom", 
        "Loại câu hỏi", 
        "Nguồn"
    ])

    ws.append(headers)

    # Format Header
    header_font = Font(color="FFFFFF", bold=True)
    header_fill = PatternFill(start_color="000080", end_color="000080", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    # Bật AutoFilter và Freeze
    ws.auto_filter.ref = f"A1:{openpyxl.utils.get_column_letter(len(headers))}1"
    ws.freeze_panes = "A2"

    # 2. Điền Data
    data_alignment = Alignment(vertical="top", wrap_text=True)

    for idx, q in enumerate(questions, 1):
        row_data = [
            idx,
            _sanitize_for_excel(q.content)
        ]

        sorted_opts = sorted(q.options, key=lambda x: x.id)
        
        correct_letters = []
        # Điền nội dung options
        for i in range(max_opts):
            if i < len(sorted_opts):
                opt = sorted_opts[i]
                row_data.append(_sanitize_for_excel(opt.content))
                if opt.is_correct:
                    correct_letters.append(chr(65 + i))
            else:
                row_data.append("") # padding

        # Đáp án đúng
        row_data.append(", ".join(correct_letters))
        
        # Các cột còn lại
        row_data.extend([
            _sanitize_for_excel(q.explanation),
            q.difficulty or "",
            q.bloom_level or "",
            q.question_type or "",
            _sanitize_for_excel(q.material.title if q.material else "N/A")
        ])

        ws.append(row_data)

        for col_num in range(1, len(headers) + 1):
            ws.cell(row=idx + 1, column=col_num).alignment = data_alignment

    # 3. Chỉnh Auto-width 
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter 
        for cell in col:
            try: 
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        adjusted_width = min((max_length + 2), 50)
        ws.column_dimensions[column].width = adjusted_width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
