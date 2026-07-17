# Báo cáo thay đổi: Task T014 - Course CRUD API

## Mức độ hoàn thành

Đã hoàn thành phần Course CRUD sử dụng PostgreSQL: migration, xóa mềm, phân trang và phân quyền mock theo owner/role.
Việc tích hợp JWT và phân quyền thật sẽ thực hiện sau khi T010/T011 hoàn thành.

## Thay đổi chính

1. **Cập nhật Database Model (`backend/app/models/course.py`)**
   - Thêm cột `is_deleted` kiểu Boolean, mặc định `False`.
   - Thêm cột `updated_at` kiểu DateTime.
   - `updated_at` được service layer gán thủ công bằng `datetime.now(timezone.utc)` khi cập nhật hoặc xóa mềm.

2. **Alembic Migration (`backend/alembic/versions bf4070a273b0_add_course_soft_delete_and_update_fields.py`)**
   - Tạo migration cập nhật cấu trúc bảng `courses`.
   - Thêm hai cột `updated_at` và `is_deleted`.
   - Có đầy đủ `upgrade()` và `downgrade()`.

3. **Dependencies (`backend/app/api/deps.py`)**
   - `get_db()`: cung cấp database session cho route.
   - `get_current_user_id() -> int`: tạm mock trả về `1`.
   - `get_current_user_role() -> str`: tạm mock trả về `"admin"`.
   - Sau khi T010/T011 hoàn thành, các dependency này sẽ được thay bằng thông tin user và role từ JWT.
   - Lưu ý: database cần có user `id = 1` để tránh lỗi foreign key khi tạo course. Trong lúc Auth/RBAC chưa hoàn thành, có thể tạo user test thủ công.

4. **Business Logic (`backend/app/services/course_service.py`)**
   - Có các hàm `create_course`, `list_courses`, `get_course`, `update_course` và `soft_delete_course`.
   - Course bị xóa mềm có `is_deleted = True` và được cập nhật `updated_at`.
   - Các truy vấn list/detail thông thường không trả course đã xóa mềm.
   - Quyền mock:
     - `admin`: xem tất cả course và có thể lọc theo `created_by`.
     - `lecturer`: chỉ xem, sửa và xóa course của chính mình.
     - Role khác: trả lỗi `403 Forbidden`.

5. **API Routes (`backend/app/api/routes/courses.py`)**
   - Đã bỏ dữ liệu in-memory.
   - Các endpoint dùng SQLAlchemy Session và service layer.
   - Có các endpoint:
     - `POST /api/v1/courses`
     - `GET /api/v1/courses`
     - `GET /api/v1/courses/{course_id}`
     - `PUT /api/v1/courses/{course_id}`
     - `DELETE /api/v1/courses/{course_id}`
   - Phân trang dùng:
     - `skip: int = Query(default=0, ge=0)`
     - `limit: int = Query(default=20, ge=1, le=100)`
   - Nếu tham số không hợp lệ, API trả `422 Validation Error`.
   - Lỗi nghiệp vụ dùng format thống nhất:
     ```json
     {"message": "..."}
     ```
     
## Phần chờ T010/T011

- Thay `get_current_user_id()` bằng user ID lấy từ JWT.
- Thay `get_current_user_role()` bằng role thật của user đăng nhập.
- Test lại quyền admin và lecturer bằng dữ liệu user thật.