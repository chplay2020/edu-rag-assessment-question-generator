# Báo cáo hoàn thành Task T046: Lưu QuestionValidationResult

## 🎯 Mục tiêu
Mục tiêu của Task T046 là lưu trữ lại kết quả kiểm định chất lượng (Validation Results) của từng câu hỏi được sinh ra bởi AI (bao gồm điểm số `score`, cảnh báo `warnings` và loại công cụ kiểm định `validator_type`). Sau đó, trả siêu dữ liệu (metadata) này về cho người dùng/Frontend thông qua API.

---

## 🛠️ Chi tiết triển khai (Những gì đã làm)

### 1. Database Model (Backend)
- Thêm model mới `QuestionValidationResult` vào file `backend/app/models/question.py`.
- Các trường thông tin bao gồm: `question_id`, `validator_type` (chuỗi), `score` (JSON), `warnings` (JSON).
- Thiết lập relationship 1-nhiều (`validation_results`) kết nối trực tiếp từ bảng `questions` sang bảng mới.

### 2. API Schema (Backend)
- Định nghĩa schema mới `QuestionValidationResultResponse` tại `backend/app/schemas/question_schema.py`.
- Tích hợp schema này vào `QuestionResponse`, giúp các API (như `GET /api/v1/jobs/{job_id}/questions` hay `GET /api/v1/questions/...`) tự động trả về mảng `validation_results` chứa toàn bộ điểm số và đánh giá.

### 3. Logic xử lý lưu trữ (Background Worker)
- Can thiệp vào file `backend/app/workers/question_worker.py`. 
- Tại thời điểm Worker chuẩn bị lưu câu hỏi mới vào DB, code sẽ bóc tách các kết quả từ 3 nguồn kiểm định khác nhau:
  - **Rule-based Validator:** Trích xuất từ `candidate.validation`.
  - **LLM Judge:** Trích xuất từ `candidate.judge` (nếu có bật tính năng Judge).
  - **Pipeline Duplicate Detector:** Lấy cảnh báo từ `candidate.notes`.
- Gắn tất cả các kết quả này vào thuộc tính `validation_results` của object Question để SQLAlchemy tự động insert vào database theo đúng Transaction.

### 4. Database Migration
- Đã chạy lệnh `alembic revision --autogenerate` để sinh ra bản migration tự động: `8c89652c423b_add_question_validation_results_table`.
- Đã thực thi `alembic upgrade head` để cập nhật cấu trúc database trong container PostgreSQL.
- Đã chạy tự động và **Pass 100% (7/7)** các Unit Test cho phần Background Worker (`pytest tests/test_question_generation_worker.py`).

---

## 🐞 Hotfixes (Lỗi đã sửa)
Trong quá trình triển khai, đã phát hiện và sửa nóng 1 lỗi nghiêm trọng trên Frontend:
- **Lỗi:** Frontend Vite bị sập (Parse Error), màn hình trắng tinh, không build được trang.
- **Nguyên nhân:** Có sự cố copy-paste làm thiếu mất dấu đóng ngoặc điều kiện JSX `)}` tại file `frontend/src/pages/MaterialDetail.tsx` (dòng 504). Lỗi này có thể do tàn dư của các Task UI trước đó để lại.
- **Cách fix:** Bổ sung lại cú pháp `)}` và code Frontend đã tải lại tự động mượt mà.

---

## 📌 Hướng dẫn Review / Test (Dành cho Leader)
1. Đảm bảo Backend container đang chạy phiên bản code mới nhất (có thể restart nếu cần).
2. Tạo thử một Job sinh câu hỏi mới (POST `/api/v1/jobs/material/{material_id}/generate-questions`).
3. Dùng `job_id` trả về để gọi API lấy danh sách câu hỏi (GET `/api/v1/jobs/{job_id}/questions`).
4. Tại cuối JSON của mỗi câu hỏi, Leader sẽ thấy xuất hiện một array `"validation_results"` chứa các metadata kiểm định, chứng minh dữ liệu đã được lưu trữ và truy xuất thành công.
