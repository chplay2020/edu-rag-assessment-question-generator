# Báo cáo thay đổi: Task T014 - Course CRUD API

## Mức độ hoàn thành

Đã hoàn thành toàn bộ Course CRUD API sử dụng PostgreSQL: migration, xóa mềm, phân trang và phân quyền thực tế theo JWT

## Phân quyền

- **`lecturer`**: tạo, xem, sửa, xóa mềm course của chính mình.
- **`admin`**: tạo và quản lý tất cả course (xem, sửa, xóa mềm mọi course, có thể lọc theo `created_by`).
- **Role không hợp lệ**: trả `403 Forbidden`.

User ID và role được lấy từ JWT thông qua các dependency trong `app/api/deps.py`:
- `get_current_user_id()` → trả `user.id` từ JWT.
- `get_current_user_role()` → trả `user.role` từ JWT.
- `get_current_active_lecturer()` → cho phép `lecturer` và `admin`.
- `get_current_active_admin()` → chỉ cho phép `admin`.

## Thay đổi chính

1. **Database Model (`backend/app/models/course.py`)**
   - Thêm cột `is_deleted` kiểu Boolean, mặc định `False`.
   - Thêm cột `updated_at` kiểu DateTime.
   - `updated_at` được service layer gán thủ công bằng `datetime.now(timezone.utc)` khi cập nhật hoặc xóa mềm.

2. **Alembic Migration (`backend/alembic/versions/bf4070a273b0_add_course_soft_delete_and_update_fields.py`)**
   - Tạo migration cập nhật cấu trúc bảng `courses`.
   - Thêm hai cột `updated_at` và `is_deleted`.
   - Có đầy đủ `upgrade()` và `downgrade()`.

3. **Dependencies (`backend/app/api/deps.py`)**
   - `get_db()`: cung cấp database session cho route.
   - `get_current_user()`: decode JWT, tra cứu user trong DB, kiểm tra `is_active`.
   - `get_current_user_id()`: trả `user.id` từ JWT.
   - `get_current_user_role()`: trả `user.role` từ JWT.
   - `get_current_active_lecturer()`: cho phép role `lecturer` và `admin`; trả `403` nếu role khác.
   - `get_current_active_admin()`: chỉ cho phép role `admin`; trả `403` nếu khác.

4. **Business Logic (`backend/app/services/course_service.py`)**
   - Các hàm: `create_course`, `list_courses`, `get_course`, `update_course`, `soft_delete_course`.
   - `created_by` được gán tự động từ `current_user_id` (JWT), client không gửi trường này.
   - Course bị xóa mềm có `is_deleted = True` và `updated_at` được cập nhật.
   - Các truy vấn list/detail không trả course đã xóa mềm.
   - Quyền theo role:
     - `admin`: xem tất cả course, lọc theo `created_by` tuỳ ý.
     - `lecturer`: chỉ xem, sửa, xóa course của chính mình (`created_by == current_user_id`).
     - Role khác: `403 Forbidden`.

5. **API Routes (`backend/app/api/routes/courses.py`)**
   - Endpoint:
     - `POST /api/v1/courses` — tạo course (yêu cầu role `lecturer` hoặc `admin`).
     - `GET /api/v1/courses` — danh sách course chưa xóa mềm.
     - `GET /api/v1/courses/{course_id}` — chi tiết course.
     - `PUT /api/v1/courses/{course_id}` — cập nhật course.
     - `DELETE /api/v1/courses/{course_id}` — xóa mềm course.
   - Phân trang:
     - `skip: int = Query(default=0, ge=0)`
     - `limit: int = Query(default=20, ge=1, le=100)`
   - Tham số không hợp lệ (ví dụ `limit=101`) trả `422 Validation Error`.
   - Không có token hoặc token không hợp lệ trả `401 Unauthorized`.
   - Lỗi nghiệp vụ dùng format thống nhất: `{"message": "..."}`.
