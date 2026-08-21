# T066: Job progress fields

## Mục tiêu (Goal)
Theo dõi tiến độ, trạng thái và lỗi của các tiến trình xử lý ngầm (background jobs) như xử lý tài liệu và sinh câu hỏi.

## Chi tiết thay đổi (Changes)
1. **Cập nhật Database Schema (Models):**
   - Bổ sung trường `percent` (kiểu số thực `Float`, mặc định là `0.0`) vào bảng `jobs` (để lưu % hoàn thành).
   - Bổ sung trường `error_message` (kiểu văn bản `Text`) để ghi nhận lỗi khi background job thất bại.
   - Bổ sung trường `started_at` (kiểu thời gian `DateTime`) để biết job bắt đầu lúc nào.
   - Viết comment bằng tiếng Việt cho các trường mới trong `app/models/material.py`.
   - Sinh file Alembic migration (`a6e2edd920b1_add_job_progress_fields.py`) và cập nhật database.

2. **Cập nhật Workers:**
   - Trong `app/workers/material_worker.py` và `app/workers/question_worker.py`, sửa đổi hàm `_set_job_status()`:
     - Khi trạng thái chuyển sang `running`, cập nhật `started_at`.
     - Cho phép nhận tham số `percent` và cập nhật vào record. Nếu trạng thái là `done`, tự động đặt `percent = 100.0`.
     - Cho phép nhận tham số `error_message` và ghi vào CSDL (bắt lỗi trong các khối `try...except`).

3. **Cập nhật API Schemas & Service:**
   - Cập nhật schema `JobResponse` (`app/schemas/material_schema.py`) để bổ sung các trường `percent`, `error_message`, `started_at`. Đặt `percent` là `Optional[float]` để giải quyết vấn đề test contract bị lỗi khi truyền đối tượng từ model.
   - Cập nhật hàm `job_summary()` trong `app/services/question_generation_service.py` để bổ sung kết xuất thông tin mới ra API.
   - Chạy kiểm thử tự động toàn bộ Backend để đảm bảo hệ thống ổn định (`151 passed`).

## Kiểm thử (Testing)
Tất cả các Unit / Integration Tests Backend liên quan đến tiến trình (Job) đã pass hoàn toàn. Front-end hoặc các thành phần Observability hiện tại có thể gọi API xem Job và nhận được số liệu theo dõi đầy đủ.
