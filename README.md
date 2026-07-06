# Báo cáo PR: Hoàn thành Task T002 & T003 (Project Foundation)

File này tóm tắt toàn bộ các thay đổi cốt lõi trong giai đoạn khởi tạo dự án để Leader dễ dàng review code trước khi merge.

## 1. Backend (Task T002: Khởi tạo FastAPI project structure)

**Định nghĩa hoàn thành (DoD): Backend chạy /health (Hoàn tất 100%)**

- **Project Structure**: Đã thiết lập cấu trúc thư mục chuẩn (`app`, `routers`, `services`, `schemas`, `core config`).
- **Core Config (`app/core/config.py`)**: Khởi tạo `pydantic-settings` để quản lý biến môi trường.
- **Global Exception Handler (`app/core/exceptions.py`)**: Đã thiết lập bộ xử lý lỗi tập trung để bắt các lỗi phổ biến (Validation, 404, 500) và trả về format chung, kèm class `AppException`.
- **Base Schema & Init**: Tạo `BaseSchema` trong `app/schemas/base.py` kế thừa từ BaseModel (với cấu hình chuẩn cho ORM) và các file `__init__.py` cho services/schemas.
- **API Router (`app/api/main.py`)**: Thiết lập router gốc để gắn các module sau này.
- **Health Check**: API `GET /health` đã hoạt động thành công tại `app/main.py`.

## 2. Frontend (Task T003: Khởi tạo React/Next.js frontend)

**Định nghĩa hoàn thành (DoD): Frontend chạy local, có layout chính (Hoàn tất 100%)**

- **Framework & Libraries**: Khởi tạo bằng Vite + React + TypeScript. Cài đặt `react-router-dom` và `axios`.
- **Global Styles (`index.css`)**: Xóa code mặc định, thiết lập hệ thống CSS Variables theo phong cách **Premium UI (Glassmorphism, font Inter, màu sắc hiện đại)**.
- **UI Components Base (`components/common/Button.tsx`)**: Tạo component nút bấm dùng chung có hỗ trợ variants (primary, secondary) và hiệu ứng hover.
- **Routing & Layout (`App.tsx`, `layouts/MainLayout.tsx`)**:
  - Thiết lập Router xử lý luồng đi giữa các trang.
  - Tạo layout chính gồm Sidebar và Header gọn gàng để render các nội dung con (Dashboard, Question Bank...).
- **Auth Guard Placeholder (`routes/AuthGuard.tsx`)**: Tạo component bọc bảo vệ route. Tạm thời dùng mock logic (`localStorage`) để chuyển hướng (redirect) người dùng chưa đăng nhập về trang Login.
- **Pages**: Xây dựng 2 trang cơ bản:
  - `Login.tsx`: Trang đăng nhập phong cách Glassmorphism mượt mà.
  - `Dashboard.tsx`: Trang tổng quan chứa giao diện thống kê giữ chỗ (placeholder).

**Ghi chú cho Reviewer**: Tất cả cấu trúc hiện tại đã sẵn sàng để tích hợp trực tiếp PostgreSQL (backend) và kết nối API (frontend) trong các Sprint tiếp theo.
