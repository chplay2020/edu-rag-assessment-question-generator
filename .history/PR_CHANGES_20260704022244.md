# PR Description: Khởi tạo Fullstack Skeleton

Dưới đây là chi tiết các thay đổi trong đợt commit này để hỗ trợ Leader và các thành viên khác trong team nắm bắt tiến độ dự án:

## Những phần đã thay đổi và Lý do

### 1. Khởi tạo Backend (FastAPI)
- **Thay đổi**: 
  - Khai báo các thư viện cần thiết (`fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `alembic`) trong `backend/requirements.txt`.
  - Khởi tạo instance FastAPI và cấu hình CORS ở file `backend/app/main.py`.
  - Thiết lập class `Settings` quản lý biến môi trường trong `backend/app/core/config.py`.
  - Tạo Router API gốc trong `backend/app/api/main.py`.
- **Lý do**: Các file rỗng ban đầu không thể chạy được. Việc thiết lập khung chuẩn của FastAPI giúp dự án sẵn sàng để chia việc (người làm API user, người làm module xử lý AI) mà không bị conflict. CORS được cấu hình mở (`*`) để frontend ở môi trường dev có thể dễ dàng gọi sang.

### 2. Khởi tạo Frontend (React + Vite + TypeScript)
- **Thay đổi**: 
  - Dọn dẹp các file rỗng ở thư mục `frontend/`.
  - Dùng `create-vite` để sinh cấu trúc thư mục React với TypeScript.
  - Cài đặt thêm thư viện `axios` (gọi API) và `react-router-dom` (chia trang).
- **Lý do**: Vite là build tool hiện đại giúp server frontend chạy cực nhanh. Việc dùng TypeScript sẽ giảm thiểu rất nhiều lỗi khi làm việc nhóm so với JavaScript thuần, đồng thời `axios` và `react-router-dom` là các công cụ gần như bắt buộc cho một ứng dụng web Single Page Application (SPA).
