# T068: Export Word optional

## Mục tiêu (Goal)
Hỗ trợ tính năng xuất danh sách câu hỏi ra định dạng Word (.docx) đơn giản, đáp ứng yêu cầu đa dạng hóa định dạng lưu trữ ngoài Excel hiện có.

## Chi tiết thay đổi (Changes)
1. **Cài đặt thư viện:**
   - Cài đặt thêm thư viện `python-docx` vào `requirements.txt` để hỗ trợ việc tạo và xử lý file Word bên trong python.
   
2. **Cập nhật Backend Services (`app/services/export_service.py`):**
   - Viết hàm mới `export_questions_to_word(db, questions, user_id, question_ids)`.
   - Hàm này sẽ lặp qua danh sách các câu hỏi, tạo các tiêu đề (Heading), sau đó liệt kê từng đáp án (A, B, C, D). Đáp án đúng sẽ tự động được **in đậm (Bold)** và *gạch chân (Underline)*.
   - Các trường như Độ khó (Difficulty), Bloom, và Giải thích (Explanation) cũng được đính kèm sau mỗi câu.
   - File kết quả `.docx` được lưu vật lý vào thư mục cấu hình chung giống như file Excel và tạo một bản ghi (record) vào DB (bảng `exports`).

3. **Cập nhật API Routes (`app/api/routes/exports.py`):**
   - Mở mới Endpoint `POST /api/v1/exports/word`. Nhận vào danh sách `question_ids` và trả ra file Word trực tiếp (luồng y hệt `/excel`).
   - Sửa đổi Endpoint Tải lại File Cũ (`GET /api/v1/exports/{export_id}/download`) để tự động trả về đúng `media_type` (Word hoặc Excel) tùy thuộc vào đuôi file.

## Kiểm thử (Testing)
- API gọi POST trực tiếp trả về file download có thể mở bằng MS Word một cách mượt mà.
- File Word xuất ra giữ đúng form chuẩn, đọc dễ hiểu, đáp án rõ ràng.

