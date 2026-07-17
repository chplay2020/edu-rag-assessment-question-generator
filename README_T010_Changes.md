# Báo cáo Thay đổi Code: Task T010 (Auth/RBAC - JWT Login)

File README này tóm tắt các tính năng đã được triển khai và những bug hệ thống đã được sửa trong Task T010, giúp Leader dễ dàng theo dõi và review PR.

## 1. Mức độ hoàn thành
**Task T010 đã hoàn thành 100%.**
- Đã triển khai thành công cơ chế mã hóa mật khẩu (Password Hashing) bằng thuật toán **Bcrypt** thông qua `passlib`.
- Đã tích hợp **JWT (JSON Web Token)** để cấp phát Access Token khi người dùng đăng nhập.
- Đã hoàn thiện 3 endpoint cốt lõi theo đúng Definition of Done (DoD): `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, và `GET /api/v1/auth/me`.

## 2. Các Bug Hệ Thống Đã Fix
Trong quá trình triển khai, đã phát hiện và xử lý dứt điểm 2 lỗi môi trường nghiêm trọng:

1. **Lỗi `exec format error` của Database trên Windows/WSL2:**
   - **Tình trạng:** Image `ankane/pgvector:v0.5.1` không tương thích kiến trúc CPU với Docker Desktop trên một số máy Windows, khiến DB sập liên tục (CrashLoop).
   - **Cách sửa:** Chuyển sang sử dụng Image chính chủ `pgvector/pgvector:pg15` trong file `docker-compose.yml`. Database đã chạy mượt mà.

2. **Lỗi `ValueError: password cannot be longer than 72 bytes` khi tạo tài khoản:**
   - **Tình trạng:** Đây là một lỗi (bug) nổi tiếng do sự xung đột giữa thư viện `passlib` (cũ) và `bcrypt` phiên bản mới (`>=4.1.0`), khiến mọi thao tác Hash mật khẩu đều văng lỗi 500 Internal Server Error.
   - **Cách sửa:** Khóa (pin) cứng phiên bản `bcrypt==4.0.1` trong `backend/requirements.txt`. Bug đã được xử lý triệt để.

## 3. Hướng dẫn Test (Dành cho Reviewer / QA)
Không cần cài đặt Postman, có thể test trực tiếp bằng tài liệu OpenAPI:

1. Khởi động hệ thống (nếu chưa chạy):
   ```bash
   docker compose up --build -d
   ```
2. Truy cập: **`http://localhost:8000/docs`**
3. **Tạo tài khoản:** Mở API `POST /api/v1/auth/register` -> Bấm *Try it out* -> Nhập email/password giả định -> Bấm *Execute*. Đảm bảo trả về mã `200`.
4. **Đăng nhập:** Bấm vào biểu tượng Ổ khóa (**Authorize**) ở góc phải trên cùng -> Nhập email/password vừa tạo -> Bấm *Authorize*.
5. **Kiểm tra Token:** Mở API `GET /api/v1/auth/me` -> Bấm *Execute*. Hệ thống sẽ nhận diện được Token và trả về đúng thông tin user hiện tại (Mã `200`).
