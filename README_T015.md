# Báo cáo thay đổi: Task T015 - Course List Page

## Mức độ hoàn thành

Đã hoàn thành phần giao diện chính cho trang danh sách môn học ở frontend theo yêu cầu của Task T015.

Hiện tại task chưa thể hoàn thiện 100% với dữ liệu thật vì còn phụ thuộc vào Course API và các phần Auth/RBAC từ task backend. Do đó frontend đang dùng mock data để đảm bảo giao diện, search và luồng điều hướng có thể chạy độc lập trong lúc chờ backend hoàn thiện/merge.

## Thông tin task

- Task ID: T015
- Tên task: Course list page
- Stream: Frontend
- Module: Course
- Priority: P0 - Must
- Dependency: Course API
- Definition of Done: Xem danh sách môn học trên UI

## Thay đổi chính

- Thêm trang danh sách môn học:
  - `frontend/src/pages/Courses.tsx`
  - `frontend/src/pages/Courses.css`

- Gắn route cho Course UI:
  - `/courses`: hiển thị danh sách môn học.
  - `/courses/:id`: mở trang chi tiết môn học dạng placeholder.

- Thêm trang chi tiết môn học tạm thời:
  - `frontend/src/pages/CourseDetail.tsx`
  - `frontend/src/pages/CourseDetail.css`

- Cập nhật layout/navigation:
  - Sidebar có mục Môn học.
  - Active state tự động theo route hiện tại.
  - Header có nút đăng xuất.

## Chức năng đã có

- Hiển thị danh sách môn học bằng mock data.
- Tìm kiếm cơ bản theo:
  - mã môn học,
  - tên môn học,
  - mô tả môn học.
- Có nút `Xem chi tiết` để điều hướng sang `/courses/:id`.
- Có trạng thái loading.
- Có empty state khi không tìm thấy kết quả tìm kiếm.
- Có fallback mock data khi backend API chưa chạy hoặc chưa trả dữ liệu.

## Lý do chưa hoàn thiện 100%

Task T015 phụ thuộc vào Course API. Tuy nhiên phần backend API liên quan hiện chưa sẵn sàng đầy đủ để frontend sử dụng ổn định trong luồng thật.

Cụ thể:

- Course API từ task backend chưa hoàn thiện.
- Auth/JWT/RBAC thật từ các task backend liên quan chưa hoàn tất, nên chưa thể lấy đúng danh sách môn học theo user đăng nhập thật.
- Dữ liệu trả về từ backend thật có thể còn thay đổi, nên frontend hiện chỉ chuẩn bị mapping cơ bản và fallback về mock data.

Vì vậy phần frontend hiện đang ở trạng thái:

- Hoàn thành UI/UX chính của T015.
- Hoàn thành luồng search và link detail.
- Chưa xác nhận dữ liệu thật từ backend production/dev API.
- Chưa thể bỏ mock data hoàn toàn.

## Cách hoạt động hiện tại

Trang `Courses` sẽ thử gọi:

```text
GET http://localhost:8000/api/v1/courses
```

Nếu API trả dữ liệu hợp lệ, frontend sẽ hiển thị dữ liệu từ backend.

Nếu API lỗi, backend chưa chạy, hoặc dữ liệu chưa đúng định dạng, frontend sẽ tự động dùng mock data để trang vẫn hiển thị được.

## Việc cần làm sau khi backend sẵn sàng

- Chạy lại backend Course API.
- Kiểm tra response thật của:
  - `GET /api/v1/courses`
  - `GET /api/v1/courses/{id}`
- Đồng bộ lại field nếu backend trả khác mock data.
- Xác nhận danh sách course theo user/role sau khi Auth/RBAC hoàn thiện.
- Cân nhắc bỏ mock data hoặc chỉ giữ mock data cho môi trường dev.
- Kiểm tra lại UI với dữ liệu thật nhiều dòng.

## Kiểm tra đã chạy

Đã kiểm tra frontend:

```bash
npm.cmd run build
npm.cmd run lint
```

Kết quả:

- Build thành công.
- Lint không báo lỗi.

## Ghi chú

Phần mock data hiện tại chỉ dùng để phục vụ phát triển frontend trong lúc chờ backend. Đây không phải dữ liệu thật và không đại diện cho dữ liệu cuối cùng của hệ thống.
