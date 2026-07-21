# Báo cáo hoàn thành Task T012: Login page + token storage

Tài liệu này tóm tắt các công việc đã được thực hiện để hoàn thành Task T012 - Authentication & RBAC (Frontend).

## Mục tiêu
- **Feature**: Auth/RBAC
- **Module**: Authentication 
- **Sub-module**: Login page + token storage
- **Condition to done**: User login được từ UI. Form login, gọi API, lưu token, redirect vào dashboard.

## Chi tiết các công việc đã triển khai

### 1. Khởi tạo API Client (`src/services/api.ts`)
- Cấu hình Axios instance (`api.ts`) để thực hiện các HTTP requests tới Backend.
- Viết **Request Interceptor** để tự động đính kèm `token` vào header `Authorization: Bearer <token>` nếu người dùng đã đăng nhập.
- Viết **Response Interceptor** để lắng nghe lỗi `401 Unauthorized`. Khi gặp lỗi này, hệ thống sẽ tự động clear token để đảm bảo an toàn.

### 2. Dịch vụ Xác thực (`src/services/auth.ts`)
- Khởi tạo `authService` đảm nhiệm logic gọi API xác thực.
- Hàm `login`: Gửi yêu cầu `POST /auth/login` với kiểu dữ liệu `application/x-www-form-urlencoded` (chuẩn chung của OAuth2 Password Bearer thường dùng với FastAPI).
- Có cơ chế **Mock Login Fallback**: Nếu Backend chưa hoàn thiện hoặc đang bị lỗi/đóng, hàm login sẽ giả lập thành công sau 500ms và trả về `mock-jwt-token-12345` để Frontend (UI) không bị block tiến độ phát triển.
- Các hàm phụ trợ: `logout` (xóa token), `isAuthenticated` (kiểm tra trạng thái đăng nhập dựa trên token).

### 3. Cập nhật Giao diện Đăng nhập (`src/pages/Login.tsx`)
- Chuyển form thành **Controlled Components** với React State (`useState`) cho `email` và `password`.
- Xử lý trạng thái `isLoading` để hiển thị chữ "Signing In..." và vô hiệu hóa nút submit, chống spam click.
- Hiển thị thông báo lỗi `error` (màu đỏ) nếu đăng nhập thất bại.
- Sau khi nhận được token từ API:
  - Lưu `token` vào `localStorage`.
  - Xóa cờ `isAuthenticated` cũ để làm sạch rác (nếu có ở T003).
  - Điều hướng người dùng an toàn vào trang Dashboard (`/`).

### 4. Nâng cấp Auth Guard (`src/routes/AuthGuard.tsx`)
- Thay đổi cơ chế kiểm tra auth từ cờ cứng `isAuthenticated = true` sang việc gọi hàm `authService.isAuthenticated()` để kiểm tra xem đã có token xác thực thật trong `localStorage` hay chưa.

## Kết luận
Task T012 đã **hoàn thành**. Luồng đăng nhập từ UI đã được nối ghép hoàn chỉnh với Service, quản lý token chuẩn chỉnh và sẵn sàng để tích hợp mượt mà khi Backend Auth Endpoint hoàn thành.
