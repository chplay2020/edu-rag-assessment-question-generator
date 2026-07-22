# Báo cáo thay đổi Code: Task T017 (Seed data & Bug Fixes)

## 1. Mức độ hoàn thành
**Task T017 đã hoàn thành 100%.**
Bên cạnh việc hoàn thành đúng Scope của T017 là tạo dữ liệu mẫu, quá trình kiểm thử đã phát hiện và xử lý triệt để 3 lỗi (bugs) nghiêm trọng tồn đọng từ các PR trước ở nhánh Frontend.

## 2. Các lỗi đã được khắc phục (Bug Fixes)

### Lỗi 1: Sai cấu hình đường dẫn API (404 Not Found)
- **Triệu chứng:** Frontend không thể gọi API Login do gọi sai đường dẫn (`/auth/login` thay vì `/api/v1/auth/login`).
- **Khắc phục:** Cập nhật biến môi trường `VITE_API_URL=http://localhost:8000/api/v1` trong file `docker-compose.yml`.

### Lỗi 2: Vòng lặp đăng nhập vô tận (Infinite Login Loop)
- **Triệu chứng:** Đăng nhập thành công, nhận JWT 200 OK nhưng bị văng ngược lại trang `/login` liên tục.
- **Nguyên nhân:** File `Login.tsx` đã đổi key lưu trữ từ `token` thành `access_token`, nhưng `api.ts` và `auth.ts` vẫn dùng tên cũ (`token`), khiến `AuthGuard` nhầm tưởng user chưa đăng nhập.
- **Khắc phục:** Đồng bộ toàn bộ logic kiểm tra và lưu JWT token trên Frontend thành `access_token` (trong `frontend/src/services/api.ts` và `frontend/src/services/auth.ts`).

### Lỗi 3: Lỗi Double Prefix `/api/v1/api/v1/courses`
- **Triệu chứng:** Frontend gọi API lấy danh sách Khóa học nhưng nhận lỗi 404.
- **Nguyên nhân:** Biến môi trường đã được gắn sẵn `/api/v1`, nhưng file `courseApi.ts` lại hardcode (cố định) thêm một lần `/api/v1/courses` nữa, tạo ra URL kép.
- **Khắc phục:** Xóa tiền tố `/api/v1` dư thừa trong toàn bộ các endpoint của `frontend/src/services/courseApi.ts`.

## 3. Dữ liệu đã được nạp (Seeding Data)
Đã tạo script Python (`backend/seed_data.py`) và wrapper (`scripts/seed_data.sh`).

**Các tài khoản đã được nạp sẵn để Test:**
1. **Quản trị viên (Admin):**
   - Email: `admin@gmail.com`
   - Mật khẩu: `admin123`
   - Role: `admin` (Dùng để test tính năng Thêm/Sửa/Xóa khóa học).

2. **Giảng viên (Lecturer):**
   - Email: `gv1@gmail.com`
   - Mật khẩu: `gv123`
   - Role: `lecturer` (Bị chặn khi tạo khóa học do Role Guard).

**Khóa học mẫu:**
- **Mã:** `CS101`
- **Tên:** Nhập môn Khoa học Máy tính
- **Mô tả:** Khóa học cơ bản về lập trình và khoa học máy tính dành cho người mới bắt đầu.
- **Người tạo:** `admin@gmail.com`

## 4. Cách chạy lại Seed Script (Nếu cần)
Chạy lệnh sau tại thư mục gốc:
```bash
docker compose exec backend python seed_data.py
```
Hoặc dùng file Bash:
```bash
bash scripts/seed_data.sh
```
