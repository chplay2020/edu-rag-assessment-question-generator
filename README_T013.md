# T013 - Protected routes + logout

## Thông tin Task
- **Task ID:** T013
- **Component:** Frontend
- **Feature:** Auth/RBAC
- **Module:** Authentication
- **Name:** Protected routes + logout
- **Mô tả:** [FE] Protected routes + logout
- **Note:** Không login không vào được app.

## Chi tiết những gì đã làm

1. **Xác thực và củng cố Protected Routes (`AuthGuard`):**
   - Đã kiểm tra và đảm bảo Component `AuthGuard` (tại `frontend/src/routes/AuthGuard.tsx`) hoạt động đúng mục đích. 
   - `AuthGuard` bọc tất cả các private routes bên trong `App.tsx` (như Dashboard `/`, Question Bank `/questions`, Courses `/courses`). 
   - Nếu người dùng truy cập vào các trang này nhưng chưa đăng nhập (không có flag `isAuthenticated` trong `localStorage`), `AuthGuard` sẽ chặn lại và tự động redirect về trang `/login`. Điều này đáp ứng chính xác yêu cầu "Không login không vào được app".

2. **Cải tiến luồng trải nghiệm tại trang Login:**
   - **Tệp chỉnh sửa:** `frontend/src/pages/Login.tsx`
   - **Thay đổi:** Thêm một `useEffect` để kiểm tra trạng thái đăng nhập ngay khi vào trang Login. Nếu người dùng **đã đăng nhập** trước đó, hệ thống sẽ tự động điều hướng họ thẳng vào trang chủ Dashboard (`/`, với `replace: true`) thay vì bắt họ xem lại form đăng nhập.

3. **Xác thực tính năng Logout:**
   - Đã kiểm tra tính năng đăng xuất tại `frontend/src/layouts/MainLayout.tsx`.
   - Hàm `handleLogout` khi người dùng bấm nút Logout ở góc phải phía trên màn hình sẽ thực hiện xóa key `isAuthenticated` khỏi `localStorage` một cách an toàn và lập tức redirect người dùng ra trang `/login`.

## Tóm tắt trạng thái
- Tính năng bảo vệ các trang không cho phép khách truy cập (Protected routes) hoạt động ổn định.
- Chức năng đăng xuất (Logout) xóa đúng state và điều hướng chính xác.
- Luồng UX được đảm bảo chặt chẽ (đã login thì không thấy màn hình login nữa, chưa login thì không vào được app).
