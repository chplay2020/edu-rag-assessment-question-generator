# Báo cáo Thay đổi Code: Task T004 (Docker Compose Local)

File README này tóm tắt những thay đổi liên quan đến việc thiết lập môi trường Docker nhằm hỗ trợ Leader dễ dàng review code và nắm bắt chính xác tiến độ.

## 1. Mức độ hoàn thành
**Task T004 đã hoàn thành 100%.**
- Đã tạo các Dockerfile riêng biệt cho cả Frontend và Backend để phục vụ riêng cho môi trường phát triển (Development).
- Đã cấu hình `docker-compose.yml` tích hợp trơn tru 3 dịch vụ: Frontend, Backend, và Database PostgreSQL (có kèm pgvector).
- Đạt Definition of Done (DoD): Chỉ cần chạy lệnh `docker compose up --build -d` là khởi động được toàn bộ môi trường mà không gặp bất cứ rào cản nào trên máy lập trình viên.

## 2. Các phần đã thay đổi trong code

### A. Backend (`backend/Dockerfile.dev`)
- **Thay đổi**: Tạo mới Dockerfile dùng Python `3.10-slim`.
- **Lý do**: Sử dụng image mỏng nhẹ của Debian để tiết kiệm dung lượng. Cờ `--reload` của `uvicorn` được thiết lập làm mặc định kết hợp với việc mount source code thông qua Docker Volumes giúp Backend tự động khởi động lại mỗi khi có sự thay đổi code (Live Reloading).

### B. Frontend (`frontend/Dockerfile.dev`)
- **Thay đổi**: Tạo mới Dockerfile dùng Node `20-slim`.
- **Lý do**: Ban đầu dự kiến dùng `node:20-alpine` cho nhẹ, nhưng để giải quyết triệt để lỗi `exec format error` thường gặp trên nhân WSL2/Docker Desktop của Windows, file cấu hình đã được linh hoạt đổi sang base `node:20-slim` (dựa trên Debian). Giúp tiến trình `npm install` và Vite server hoạt động ổn định nhất trên mọi hệ điều hành. Lệnh mặc định là `npm run dev -- --host` có hỗ trợ Hot Module Replacement (HMR).

### C. Cấu hình mạng và DB (`docker-compose.yml`)
- **Thay đổi**: 
  1. Cấu hình cổng mạng (Ports) chuẩn: Frontend (`5173`), Backend (`8000`), Database (`5432`).
  2. Nâng cấp image DB từ PostgreSQL thuần lên `ankane/pgvector:v0.5.1`.
- **Lý do**: 
  1. Các services liên lạc nội bộ dễ dàng qua mạng nội bộ Docker.
  2. Dùng pgvector ngay từ bước khởi tạo để chuẩn bị sẵn sàng nền tảng Database cho việc tìm kiếm vector AI RAG ở các Sprints tiếp theo, tránh đập đi xây lại cấu trúc Database.
