# Báo cáo hoàn thành Task T050: AIModelLog token/latency/cost estimate

## 🎯 Mục tiêu
Đo lường chính xác mức độ "ngốn" tài nguyên của AI. Task T050 bổ sung khả năng đo thời gian phản hồi (latency), chi tiết số lượng token input/output, và đặc biệt là quy đổi token ra "tiền tươi thóc thật" (cost estimate). Đồng thời, mọi lỗi phát sinh từ phía AI (timeout, quá tải) cũng sẽ được ghi log lại để tiện cho việc thống kê độ ổn định.

---

## 🛠️ Chi tiết triển khai (Những gì đã làm)

### 1. Nâng cấp Database Model (AiLog)
- **File:** `backend/app/models/system.py`
- **Chi tiết:** Xóa cột `tokens_used` cũ để thay bằng dàn cột chi tiết hơn:
  - `prompt_tokens` (Int): Token đầu vào.
  - `output_tokens` (Int): Token đầu ra.
  - `total_tokens` (Int): Tổng số Token.
  - `latency_ms` (Int): Thời gian LLM xử lý tính bằng mili-giây.
  - `error` (Text): Chứa thông báo lỗi nếu gọi API thất bại.
  - `cost_estimate` (Float): Số tiền ước tính bằng USD.

### 2. Provider API & Thời gian (Latency)
- **File:** `backend/app/ai/llm/base.py` & `backend/app/ai/llm/gemini_provider.py`
- **Chi tiết:** Bổ sung `latency_ms` vào Data Class `LLMResponse`. Dùng hàm `time.perf_counter()` của Python bọc quanh lời gọi `generate_content()` để đo thời gian phản hồi thực tế của Gemini.

### 3. Ước tính chi phí & Bắt lỗi AI
- **File:** `backend/app/ai/generation/question_generator.py`
- **Chi tiết:**
  - **Bắt lỗi (Error Handling):** Bọc hàm gọi LLM vào `try...except`. Nếu LLM Provider báo lỗi (rate limit, timeout), tiến trình sẽ kết thúc sớm, nhưng vẫn tạo ra một bản record log chứa `error_msg` và thời gian treo (latency) để đẩy xuống DB.
  - **Tính tiền (Cost Estimation):** Tùy vào giá trị `model_name` (Flash hay Pro), hệ thống sẽ nhân số token với đơn giá public của Google (VD: Flash là `$0.075/1M input`) để ra con số USD tương ứng. Con số này được đẩy vào cột `cost_estimate`.

### 4. Background Worker (Lưu DB)
- **File:** `backend/app/workers/question_worker.py`
- **Chi tiết:** Cập nhật script chèn dữ liệu vào bảng `ai_logs`, mapping đủ 6 cột mới vào SQLAlchemy model.

### 5. Migrations & Testing
- Đã tạo Alembic migration `32cae1734f4e_add_advanced_logging_fields_to_ai_logs.py`.
- Apply (upgrade) DB thành công, không gặp lỗi.
- Chạy 100% Pass bộ Test (`pytest tests/test_question_generation_worker.py`), chứng minh việc bổ sung log không làm hỏng luồng AI Pipeline có sẵn.

---

## 📌 Hướng dẫn Review / Test
- Hệ thống đã sẵn sàng cung cấp đủ dữ liệu về Latency/Cost/Error cho bất kỳ Dashboard thống kê nào trong tương lai.
- Bạn có thể sinh thử vài câu hỏi rồi mở Database, kiểm tra xem bảng `ai_logs` có hiển thị giá trị dạng `0.00015` ở cột `cost_estimate` hay không.
