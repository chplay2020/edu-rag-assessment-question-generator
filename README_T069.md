# T069: Duplicate against full bank

## Mục tiêu (Goal)
Tăng cường khả năng phát hiện câu hỏi trùng lặp trong hệ thống AI/RAG. Thay vì chỉ kiểm tra trùng trong lô (batch) đang sinh, hệ thống sẽ dò tìm và cảnh báo nếu câu hỏi mới sinh có nội dung trùng khớp với các câu hỏi **đã được duyệt (approved)** nằm rải rác trong cùng một khóa học (course).

## Chi tiết thay đổi (Changes)
1. **Mở rộng Vector Store (`qdrant_store.py`)**:
   - Đưa trường `status` vào danh sách `INDEXED_PAYLOAD_FIELDS` để Qdrant có thể tạo chỉ mục và tra cứu tốc độ cao.
   - Cập nhật logic của `build_question_filter()` và `search_questions()` để hỗ trợ lọc theo trạng thái của câu hỏi (ở đây là truyền `status="approved"`).

2. **Tinh chỉnh Duplicate Detector (`duplicate_detector.py`)**:
   - Nâng cấp hàm `detect_duplicate_question` bằng cách truyền tham số `status="approved"` xuống dưới khi gọi `search_questions`. Nhờ đó, tính năng chống trùng sẽ tự động thu hẹp phạm vi kiểm tra, tập trung phát hiện lỗi trùng ý tưởng với các câu hỏi đang dùng thực tế, bỏ qua các câu nháp hay lỗi.

3. **Cập nhật Thông báo người dùng (`pipeline.py`)**:
   - Cập nhật cảnh báo: *“Có thể trùng với câu hỏi đã duyệt trong ngân hàng.”* để giảng viên nhận thức được rằng câu này không phải lỗi format mà là lỗi đụng hàng với ngân hàng hiện tại.

## Kiểm thử (Testing)
- Chạy toàn bộ Unit/Integration tests cho AI Pipeline: Pass 100%. Lớp Vector Database nhận tham số filter không làm phá vỡ chức năng cũ.

