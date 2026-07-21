# Báo cáo Thay đổi Code: Task T011 (Auth/RBAC - Role Guards)

File README này tóm tắt việc triển khai hệ thống Phân quyền (Role-Based Access Control) để bảo vệ các API dựa trên vai trò của người dùng.

## 1. Mức độ hoàn thành
**Task T011 đã hoàn thành 100%.**
- Đã xây dựng thành công các dependency middlewares để chặn người dùng không đủ quyền hạn.
- Đã áp dụng Guard vào các API mẫu để chứng minh hoạt động thực tế. Đạt DoD (API bị chặn đúng khi thiếu token hoặc sai role).

## 2. Chi tiết triển khai

### A. Định nghĩa Role Guards (`backend/app/api/deps.py`)
- Khởi tạo `get_current_active_admin`: Hàm này sẽ bóc tách Token, lấy thông tin User. Nếu `role != "admin"`, nó sẽ ném ra lỗi `403 Forbidden` và lập tức ngắt request.
- Khởi tạo `get_current_active_lecturer`: Hàm này chấp nhận cả `lecturer` và `admin`. Nếu user là một học sinh/user bình thường, request sẽ bị từ chối.

### B. Tích hợp vào Routers
Để các Guard hoạt động, chỉ cần thêm `dependencies=[Depends(...)]` vào tham số của Router. Rất gọn gàng và không làm bẩn code logic bên trong.
- **`courses.py`**: API `POST /api/v1/courses` (Tạo khóa học) đã được gắn `get_current_active_admin`. Chỉ Admin mới được tạo khóa học.
- **`materials.py`**: API `POST /api/v1/materials/upload` đã được gắn `get_current_active_lecturer`. Chỉ Giảng viên (và Admin) mới được upload tài liệu.

## 3. Hướng dẫn Test (Dành cho Reviewer / QA)
Bạn có thể dễ dàng test trực tiếp trên **`http://localhost:8000/docs`**:

1. **Test không có Token (Chưa đăng nhập):**
   - Không bấm nút Authorize. Cố gắng chạy `POST /api/v1/courses`.
   - Kết quả mong muốn: Trả về lỗi `401 Unauthorized`.

2. **Test Sai Quyền (Sai Role):**
   - Đăng ký một tài khoản mặc định (ví dụ `test@gmail.com`). Hệ thống set role mặc định là `lecturer`.
   - Đăng nhập (Authorize) bằng tài khoản đó.
   - Thử chạy `POST /api/v1/courses` (Yêu cầu Admin).
   - Kết quả mong muốn: Trả về lỗi `403 Forbidden` kèm dòng thông báo "Không đủ quyền truy cập (yêu cầu Admin)".

3. **Test Đúng Quyền:**
   - Dùng tài khoản `lecturer` đó, thử chạy API `POST /api/v1/materials/upload` (Yêu cầu Lecturer).
   - Kết quả mong muốn: Trả về `200 OK` và nội dung file ảo.
