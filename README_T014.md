# Báo cáo thay đổi: Task T014 - Course CRUD API (Hoàn thành)

## Mức độ hoàn thành
Đã hoàn thành chuyển đổi toàn bộ hệ thống Course CRUD từ bộ nhớ tạm (in-memory skeleton) sang lưu trữ cơ sở dữ liệu thật sử dụng SQLAlchemy (PostgreSQL) kết hợp Alembic migrations và cơ chế phân quyền (Owner/Role) cơ bản.

## Thay đổi chính
1. **Cập nhật Database Model (`backend/app/models/course.py`)**:
   - Thêm cột `is_deleted` (Boolean, `nullable=False`, mặc định là `False`, có `server_default="false"` trong migration để tránh lỗi dữ liệu cũ).
   - Thêm cột `updated_at` (DateTime, hỗ trợ cập nhật thời gian tự động qua `onupdate=func.now()`).

2. **Alembic Migration (`backend/alembic/versions/bf4070a273b0_add_course_soft_delete_and_update_fields.py`)**:
   - Tạo migration cập nhật cấu trúc bảng `courses`.
   - Chứa đủ hàm `upgrade()` và `downgrade()` để đảm bảo tính toàn vẹn của database.

3. **Dependencies mới (`backend/app/api/deps.py`)**:
   - `get_db()`: Cung cấp database session cho các router.
   - `get_current_user_id() -> int`: Mock tạm thời trả về `1` (sẽ được thay bằng JWT decode/Auth ở T010/T011).
   - `get_current_user_role() -> str`: Mock tạm thời trả về `"admin"` (sẽ được thay bằng Auth dependency ở T010/T011).

4. **Business Logic (`backend/app/services/course_service.py`)**:
   - Viết các hàm CRUD đồng bộ (synchronous): `create_course`, `list_courses`, `get_course`, `update_course`, và `soft_delete_course`.
   - **Xử lý xóa mềm**: Khi xóa khóa học, chỉ chuyển trạng thái `is_deleted` sang `True` và cập nhật `updated_at`. Khóa học bị xóa mềm sẽ bị lọc bỏ khỏi các truy vấn thông thường.
   - **Xử lý phân quyền (Owner/Role)**:
     - `admin`: Xem được tất cả khóa học và có thể lọc theo `created_by`.
     - `lecturer`: Chỉ xem được khóa học của bản thân (`created_by == current_user_id`). Nếu lecturer cố gắng xem, sửa hoặc xóa khóa học của người khác, API sẽ trả về lỗi `404 Course not found`.
     - Các role khác: Trả về lỗi `403 Forbidden`.

5. **API Routes (`backend/app/api/routes/courses.py`)**:
   - Xóa bỏ dữ liệu dict lưu tạm. Tích hợp trực tiếp với các dependency và service.
   - Hạn chế số lượng dòng trả về trong `GET /courses` bằng cách dùng `limit: int = Query(default=20, le=100)`. Nếu client truyền giá trị > 100, FastAPI sẽ tự động trả lỗi validation `422 Unprocessable Entity`.

---

## Hướng dẫn chạy và kiểm thử

### 1. Khởi động Database (Docker PostgreSQL)
Hãy chắc chắn Docker daemon và container database đã được khởi chạy:
```bash
docker compose up -d
```
Nếu có lỗi do Docker chưa mở, vui lòng khởi động ứng dụng Docker Desktop trên máy trước.

### 2. Áp dụng Database Migration
Chạy lệnh sau tại thư mục `backend` để cập nhật cấu trúc bảng `courses`:
```bash
cd backend
.\venv\Scripts\python.exe -m alembic upgrade head
```

### 3. Chạy Backend Server
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 4. Kiểm thử qua Swagger UI
Mở trình duyệt truy cập: `http://127.0.0.1:8000/docs`

1. **Kiểm tra limit:**
   - Gọi `GET /api/v1/courses` với tham số `limit = 101`. Hệ thống phải trả về mã lỗi `422` (Validation Error).
2. **Kiểm tra CRUD ở quyền `admin` (mặc định):**
   - Thực hiện `POST /api/v1/courses` để tạo khóa học mới.
   - Gọi `GET /api/v1/courses` để kiểm tra danh sách.
   - Gọi `PUT /api/v1/courses/{id}` để cập nhật thông tin và kiểm tra `updated_at` trong response.
   - Gọi `DELETE /api/v1/courses/{id}` để xóa mềm.
   - Gọi lại `GET` (detail và list) để kiểm tra rằng khóa học đã bị lọc bỏ (không trả về).
3. **Kiểm tra phân quyền `lecturer`:**
   - Sửa tạm thời hàm `get_current_user_role` trong `backend/app/api/deps.py` để return `"lecturer"`.
   - Đảm bảo bạn chỉ lấy ra danh sách khóa học của chính mình (có `created_by == 1`).
   - Thử GET/PUT/DELETE một khóa học của user khác (ví dụ `created_by == 2` nếu có) để kiểm tra lỗi `404 Course not found`.
4. **Kiểm tra lỗi 403 Forbidden:**
   - Sửa hàm `get_current_user_role` thành role khác (ví dụ `"student"`).
   - Truy cập bất kỳ endpoint nào của Course API phải nhận về mã lỗi `403 Forbidden`.
