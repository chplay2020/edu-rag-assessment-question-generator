# T070: Integration test full flow

## Mục tiêu
Kiểm thử toàn bộ luồng hoạt động (full flow) của hệ thống: từ Upload -> Process -> Generate -> Validate (khi generate) -> Review -> Export, đảm bảo các endpoint kết nối thành một quy trình trơn tru.

## Chi tiết triển khai
1. **Tạo Test File Mới**: Đã tạo ackend/tests/test_full_integration_flow.py.
2. **Kỹ thuật Mocking**:
   - Sử dụng monkeypatch để ghi đè BackgroundTasks.add_task, biến các tác vụ chạy ngầm (xử lý tài liệu và sinh câu hỏi) thành xử lý đồng bộ ngay lập tức để thuận lợi cho việc kiểm thử API nối tiếp.
   - Mock các service bên thứ ba (Qdrant, LLM) để hệ thống chạy nhanh và không phụ thuộc vào cấu hình môi trường ngoài. 
   - Override pipeline.generate_questions_for_material để trả về câu hỏi giả định ngay lập tức với validation thành công.
3. **Các Bước Của Test Flow**:
   - POST /api/v1/materials/upload: Upload material giả lập.
   - POST /api/v1/materials/{id}/process: Chạy worker xử lý tài liệu.
   - POST /api/v1/jobs/material/{id}/generate-questions: Chạy worker sinh câu hỏi.
   - GET /api/v1/questions?course_id=...: Lấy danh sách câu hỏi đang ở trạng thái review_required.
   - POST /api/v1/questions/{q_id}/review: Approve câu hỏi.
   - POST /api/v1/exports/word: Xuất Word câu hỏi đã duyệt.

## Kết quả
- Toàn bộ pipeline đã Passed integration test (1 passed trong pytest).
- Luồng dữ liệu chạy mượt mà xuyên suốt từ frontend -> backend -> DB -> Workers -> File xuất.
