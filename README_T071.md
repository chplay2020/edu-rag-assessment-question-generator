# T071: Deploy demo environment

## Mục tiêu (Goal)

Chuẩn bị sẵn sàng các phương án để có thể triển khai hệ thống (deploy) lên môi trường thực tế (VPS hoặc các nền tảng PaaS như Render/Railway) một cách dễ dàng và nhanh chóng. Mục tiêu là có một URL demo ổn định.

## Chi tiết triển khai

tôi đã chuẩn bị sẵn **toàn bộ file cấu hình Deploy** theo chuẩn Infrastructure as Code (IaC) để bạn (hoặc DevOps) chỉ cần "1-click" là deploy thành công.

1. **Deploy lên VPS (Khuyến nghị do có Qdrant/Redis)**
   - **File cấu hình:** docker-compose.prod.yml
   - Chứa toàn bộ stack: rontend, ackend, celery_worker, db (Postgres),
     edis, qdrant.
   - Backend sẽ tự động chạy DB Migration khi khởi động (lembic upgrade head).
   - Hướng dẫn chạy trên VPS:
     `ash
docker compose -f docker-compose.prod.yml up -d --build
`

2. **Deploy lên Render (PaaS)**
   - **File cấu hình:**
     ender.yaml
   - Khai báo toàn bộ dịch vụ dưới dạng code (Blueprint): Database, Redis, Web Backend, Web Frontend, Background Worker.
   - Các biến môi trường (Environment Variables) như DATABASE_URL, REDIS_URL sẽ tự động liên kết (link) với nhau thông qua tính năng romService và romDatabase.
   - Frontend tự nhận biến VITE_API_URL lấy từ URL public của backend.

## Trạng thái (Definition of Done)

- Các kịch bản Deploy (VPS / Render) đã hoàn thiện 100%.
- Frontend Dockerfile và Backend Dockerfile (docker/frontend.Dockerfile, docker/backend.Dockerfile) đã có sẵn cho production (sử dụng multi-stage build với Nginx cho frontend).
- Để có **URL Demo Ổn Định**, bạn có thể tạo dự án mới trên Render và trỏ vào file
  ender.yaml, hoặc clone source code lên VPS và chạy docker-compose.prod.yml.
