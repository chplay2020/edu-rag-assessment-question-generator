# Frontend - Hệ thống sinh câu hỏi đánh giá năng lực tự động

Đây là thư mục chứa mã nguồn Frontend cho dự án "Hệ thống sinh câu hỏi đánh giá năng lực tự động từ học liệu điện tử bằng mô hình ngôn ngữ lớn".

## Tiến độ công việc thực hiện (Theo yêu cầu T002)

**Nhiệm vụ:** Khởi tạo React/Next.js frontend, tạo routing, layout, auth guard placeholder, UI components base.

Các công việc đã hoàn thành:
- **Khởi tạo dự án:** Sử dụng Vite + React + TypeScript làm nền tảng frontend nhanh và nhẹ.
- **Routing:** Đã thiết lập `react-router-dom` trong `src/App.tsx` bao gồm các public route (`/login`) và protected route.
- **Layout:** Đã xây dựng `MainLayout` trong `src/layouts/MainLayout.tsx` làm khung giao diện chính.
- **Auth Guard:** Đã tạo placeholder `AuthGuard` tại `src/routes/AuthGuard.tsx` dùng để kiểm tra quyền truy cập cho các route yêu cầu đăng nhập.
- **UI Components Base:** Đã tạo cấu trúc cho các UI component dùng chung tại `src/components/common/` (hiện có `Button.tsx`).
- **Pages (Trang cơ bản):** Đã tạo trang cơ sở ban đầu (`Login.tsx`, `Dashboard.tsx`).

## Cấu trúc thư mục

- `src/assets/`: Chứa tài nguyên tĩnh (hình ảnh, icons...).
- `src/components/`: Chứa các UI components, thư mục `common/` cho các thành phần dùng chung.
- `src/layouts/`: Chứa layout giao diện chính của ứng dụng (`MainLayout`).
- `src/pages/`: Chứa các trang chính tương ứng với từng route.
- `src/routes/`: Chứa các logic liên quan đến routing (`AuthGuard`).

## Hướng dẫn chạy dự án (Local)

1. **Cài đặt phụ thuộc:**
   ```bash
   npm install
   ```

2. **Chạy ứng dụng:**
   ```bash
   npm run dev
   ```
   Mở trình duyệt và truy cập địa chỉ cung cấp bởi Vite (ví dụ: `http://localhost:5173`).
