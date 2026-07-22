# README T019 – Material Upload API

## Mục tiêu
Hoàn thiện chức năng API upload tài liệu cho các khóa học (Material Upload API), bao gồm các tính năng xử lý file, lưu trữ, và phân quyền truy cập.

## Các endpoint đã hoàn thành
1. `POST /api/v1/materials/upload`: Upload file tài liệu.
2. `GET /api/v1/materials/course/{course_id}`: Lấy danh sách tài liệu theo ID khóa học.

## Quyền hạn (RBAC)
- **Lecturer**: Chỉ được phép upload và xem danh sách tài liệu của các khóa học mà mình quản lý (sở hữu).
- **Admin**: Được toàn quyền thao tác (upload, xem danh sách) trên mọi khóa học.

## Định dạng file hỗ trợ
- PDF (`.pdf`)
- DOCX (`.docx`)
- TXT (`.txt`)

## Giới hạn
- **Dung lượng**: Tối đa 10 MB mỗi file.

## Vị trí lưu trữ
- File tài liệu được lưu tại thư mục: `backend/storage/uploads/`
- `file_url` được trả về có định dạng: `/storage/uploads/<uuid>.<extension>` (hỗ trợ static file download).

## Trạng thái (Status) của Material
- PROCESSING: Tài liệu đã được tải lên và đang chờ bước xử lý nội dung/chunking/AI ở task sau.

## Hướng dẫn test
1. **Khởi động backend**: Chạy dự án qua Docker Compose hoặc trực tiếp (vd: `docker-compose up -d`).
2. **Swagger UI**: Truy cập `http://localhost:8000/docs`. Xác thực (Authorize) và thử gọi các API trong tag `materials`.
3. **Postman**: 
   - Import file `docs/EduRAG_Postman_Collection.json`.
   - Gọi `Login` để lấy và gán token tự động.
   - Gọi `Create Course` để tạo khóa học mới.
   - Gọi `Upload Material` với thông tin `course_id` vừa tạo và chọn đính kèm `file`.
   - Gọi `Get Materials By Course` để xác nhận dữ liệu đã được lưu trữ chính xác.

## Kết quả test đã xác nhận
- [x] Upload file hợp lệ (PDF/DOCX/TXT dưới 10MB) thành công.
- [x] GET danh sách đọc từ database thật, sắp xếp tài liệu mới nhất trước.
- [x] Link `file_url` tải file hoạt động tốt.
- [x] File không hợp lệ (ví dụ: `.mp4`) bị chặn với lỗi HTTP 400.
- [x] File vượt quá giới hạn 10 MB bị chặn với lỗi HTTP 400.
- [x] Lecturer cố upload tài liệu vào course của Admin sẽ bị chặn với lỗi HTTP 404 (Không tìm thấy course thuộc sở hữu).

## Giới hạn còn lại
- Chưa có giao diện (frontend) cho chức năng upload material.
- Chưa có API xóa material.
- Chưa tích hợp xử lý nội dung file, chunking, hay nhúng AI/RAG.
