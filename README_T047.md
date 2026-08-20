# Báo cáo hoàn thành Task T047: Endpoint re-validate question

## 🎯 Mục tiêu
- Tự động chạy lại quy trình kiểm định chất lượng (validation) sau khi câu hỏi được người dùng (giảng viên) chỉnh sửa thủ công.
- Cập nhật kết quả kiểm định mới nhất vào database (bảng `question_validation_results`).

---

## 🛠️ Chi tiết triển khai (Những gì đã làm)

### 1. Service Re-validate
- Đã tạo file **`backend/app/services/question_validation_service.py`**.
- Xây dựng hàm `revalidate_question` có nhiệm vụ:
  - Bóc tách nội dung câu hỏi hiện tại và các phương án (options).
  - Gọi hàm **Rule-based Validator** để bắt lỗi định dạng (format), thiếu giải thích, lộ đáp án.
  - Gọi hàm **Duplicate Detector** để truy vấn vector Qdrant xem câu hỏi có trùng lặp với các câu khác hay không. 
  - Lưu kết quả mới đè lên kết quả cũ (`validator_type="rule_based"`) vào database.

### 2. Tối ưu logic check Duplicate
- Đã sửa file **`backend/app/ai/validation/duplicate_detector.py`**:
  - Bổ sung tham số `exclude_question_id` vào hàm `detect_duplicate_question`. 
  - Việc này để bỏ qua vector của chính câu hỏi đang được đánh giá khi query Qdrant (nếu không Qdrant sẽ luôn báo là câu hỏi bị trùng 100% với chính nó).

### 3. Tích hợp ngầm vào API Update Question
- Đã chỉnh sửa **`backend/app/api/routes/questions.py`** tại endpoint `PUT /{question_id}`:
  - Bổ sung logic cho phép update danh sách các lựa chọn (`options`) của câu hỏi (xóa options cũ, insert options mới).
  - Bổ sung lệnh gọi hàm `revalidate_question` ngay trước khi commit database.
  - Nhờ thiết kế này, Frontend không cần phải gọi 2 request riêng biệt. Việc lưu chỉnh sửa sẽ lập tức cập nhật lại trạng thái cảnh báo của câu hỏi đó mà không cần thông qua LLM Judge (tiết kiệm thời gian, API quota).

## ✅ Trạng thái
- **Hoàn thành 100%**. Sẵn sàng cho việc review và test tích hợp.
