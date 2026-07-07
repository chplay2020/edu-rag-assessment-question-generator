# Báo cáo thay đổi: Task T014 - Course CRUD API

## Mức độ hoàn thành
Đã hoàn thành phần API contract/skeleton cho Course CRUD để có thể test trước trên Swagger `/docs`.

## Thay đổi chính
- Thêm schema cho Course CRUD:
  - `CourseCreate`
  - `CourseUpdate`
  - `CourseResponse`
  
- Thêm các endpoint Course CRUD:
  - `POST /api/v1/courses`
  - `GET /api/v1/courses`
  - `GET /api/v1/courses/{course_id}`
  - `PUT /api/v1/courses/{course_id}`
  - `DELETE /api/v1/courses/{course_id}`
- Đăng ký `courses` router vào `backend/app/api/main.py` để hiển thị trên Swagger `/docs`.
- Không nhận `created_by` từ client trong request tạo course; backend sẽ lấy từ user đăng nhập. Hiện tại tạm gán `created_by = 1` vì Auth/RBAC chưa được tích hợp.
- Khai báo response `404` cho các endpoint detail/update/delete để OpenAPI docs đầy đủ hơn.

## Cách test hiện tại
Chạy backend:
powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload

Mở Swagger:
text
http://127.0.0.1:8000/docs

Test nhanh:
1. Tạo course bằng `POST /api/v1/courses`.
2. Xem danh sách bằng `GET /api/v1/courses`.
3. Xem chi tiết bằng `GET /api/v1/courses/{course_id}`.
4. Sửa course bằng `PUT /api/v1/courses/{course_id}`.
5. Xóa mềm course bằng `DELETE /api/v1/courses/{course_id}`.

## Lưu ý
- Hiện tại API đang dùng dữ liệu tạm trong memory để test contract, chưa lưu DB thật.
- Dữ liệu sẽ mất khi backend reload/restart.
- Phần kết nối database, soft delete bằng DB, filter owner/role và phân quyền thật sẽ hoàn thiện sau khi T005 database model/migration và Auth/RBAC được merge.
