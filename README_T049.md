# Báo cáo hoàn thành Task T049: Prompt Versioning

## 🎯 Mục tiêu
Mục tiêu của Task T049 là lưu vết (log) lại chính xác phiên bản prompt (prompt version), tên model AI, số lượng token tiêu thụ, và cấu hình sinh câu hỏi (generation config) mỗi khi AI thực thi nhiệm vụ. Điều này giúp hệ thống truy xuất được câu hỏi nào được sinh ra bởi version prompt nào, hỗ trợ rất lớn cho việc audit, phân tích chi phí và A/B testing chất lượng AI sau này.

---

## 🛠️ Chi tiết triển khai (Những gì đã làm)

### 1. Database Model (Cấu trúc DB)
- **File:** `backend/app/models/system.py`
- **Chi tiết:** Mở rộng bảng `ai_logs` có sẵn. Bổ sung thêm các cột:
  - `job_id`: Khóa ngoại (Foreign Key) liên kết trực tiếp với bảng `jobs`. Giúp truy ngược từ một tiến trình sinh (job) ra tất cả các log AI của tiến trình đó.
  - `prompt_version`: Kiểu String, lưu phiên bản (vd: `v2`, `v3`).
  - `generation_config`: Kiểu JSON, lưu cấu hình lúc sinh (số lượng, độ khó, bloom level, ngôn ngữ).
- **File:** `backend/app/models/material.py`
- **Chi tiết:** Thêm relationship `ai_logs` vào model `Job` để truy xuất ngược hai chiều.

### 2. Output Parser (Định dạng dữ liệu nội bộ)
- **File:** `backend/app/ai/generation/output_parser.py`
- **Chi tiết:** Sửa schema `GeneratedQuestionBatch` để nó mang theo một mảng `logs` (chứa các dict metadata). Nhờ vậy, thông tin log không bị thất lạc khi truyền từ tầng LLM lên tầng Pipeline.

### 3. AI Pipeline & Generator (Thu thập Log)
- **File:** `backend/app/ai/generation/question_generator.py`
  - Đổi phương thức gọi Gemini từ `generate_text()` (chỉ lấy text) sang `generate()` (lấy toàn bộ object `LLMResponse`).
  - Trích xuất: `prompt_tokens`, `output_tokens`, `model`, và nạp cùng config, prompt_version vào một dict log. Gắn dict này vào `GeneratedQuestionBatch.logs`.
- **File:** `backend/app/ai/pipeline.py`
  - Bổ sung `ai_logs` vào `GenerationOutcome`.
  - Hứng mảng `logs` từ Generator và đút vào `outcome.ai_logs`.

### 4. Background Worker (Lưu DB)
- **File:** `backend/app/workers/question_worker.py`
- **Chi tiết:** Khi kết thúc việc xử lý và tiến hành lưu câu hỏi vào DB, Worker sẽ duyệt qua mảng `outcome.ai_logs`. Với mỗi phần tử, nó sẽ khởi tạo một instance `AiLog` và lưu vào DB cùng chung trong một Session Transaction.

### 5. Migrations & Testing
- Đã sinh tự động bản Alembic migration: `28bfc0e851c6_add_versioning_to_ai_logs.py`.
- Đã Upgrade database lên head.
- Đã chạy thành công 100% (7/7 Pass) bộ Unit Test của phần Question Worker (`pytest tests/test_question_generation_worker.py`), đảm bảo logic lưu DB mới không phá vỡ transaction cũ.

---

## 📌 Hướng dẫn Review / Test
Để kiểm chứng tiến trình này hoạt động:
1. Thông qua UI (hoặc Postman), tiến hành tạo lệnh Sinh câu hỏi mới cho một Material bất kỳ.
2. Mở DBeaver/pgAdmin (hoặc SSH vào container database), query bảng `ai_logs`.
3. Bạn sẽ thấy ngay một (hoặc nhiều) dòng dữ liệu mới. Trong đó, cột `prompt_version` sẽ ghi nhận giá trị thực tế của hệ thống (ví dụ `v2`), cột `tokens_used` báo cáo số token LLM đã tiêu thụ, cột `job_id` chỉ đích danh Job nào gọi AI, và cột `generation_config` chứa đoạn JSON cấu hình sinh.
