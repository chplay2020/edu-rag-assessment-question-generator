# Báo cáo Thay đổi Code: Task T009 (Soạn OpenAPI/API Contract)

File README này cung cấp tổng quan về các thay đổi trong việc thiết lập hợp đồng API (API Contract) để Leader dễ dàng review và team Frontend có tài liệu tham khảo.

## 1. Mức độ hoàn thành
**Task T009 đã hoàn thành 100%.**
- Đã thiết lập thành công API Contract cho 6 module cốt lõi: Auth, Courses, Materials, Jobs, Questions, Exports.
- Đạt Definition of Done (DoD): Giao diện Swagger UI (tại `/docs`) và file `openapi.json` đã được sinh ra tự động. Frontend có thể dùng ngay các mock data trả về để tiến hành dựng UI.

## 2. Chi tiết triển khai

### A. Định nghĩa Pydantic Schemas (`backend/app/schemas/`)
- Thay vì chỉ viết API chung chung, hệ thống đã được xây dựng bằng cách định nghĩa chặt chẽ Input/Output thông qua Pydantic.
- Đã tạo các files: `auth_schema.py`, `course_schema.py`, `material_schema.py`, `question_schema.py`, `export_schema.py`.
- **Lý do**: Đảm bảo Backend có bộ Validator tự động cực mạnh. Bất kỳ request nào từ Frontend gửi lên sai cấu trúc (thiếu trường, sai kiểu dữ liệu) sẽ bị FastAPI chặn đứng ngay lập tức và trả về lỗi 422 rõ ràng.

### B. Khởi tạo API Routers (`backend/app/api/routes/`)
- Đã chia nhỏ API thành các file độc lập tương ứng với từng module: `auth.py`, `courses.py`, `materials.py`, `jobs.py`, `questions.py`, `exports.py`.
- Mỗi endpoint đều đã được khai báo thuộc tính `response_model` và trả về Mock Data chuẩn xác theo đúng kiểu dữ liệu.
- **Lý do**: Giúp hệ thống tự động sinh ra OpenAPI documentation cực kỳ chi tiết. Frontend không cần đợi Backend code xong logic Database, chỉ cần gọi vào các endpoint này là đã nhận được JSON data ảo (Mock) để ghép giao diện.

### C. Tích hợp Router (`backend/app/api/main.py`)
- Gom toàn bộ các routers con vào `api_router` và gắn prefix (ví dụ: `/courses`, `/auth`) cùng thẻ `tags` để Swagger UI tự động phân nhóm API trực quan cho lập trình viên dễ đọc.
