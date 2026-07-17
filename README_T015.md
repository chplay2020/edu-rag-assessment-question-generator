# Báo cáo thay đổi: Task T015 - Course List Page

## Mức độ hoàn thành

Đã hoàn thành phần giao diện và tích hợp API cho trang danh sách môn học (T015).

Frontend hiện ưu tiên lấy dữ liệu thật từ `GET /api/v1/courses` (Course API T014). Nếu backend chưa chạy hoặc API lỗi, trang tự động fallback về mock data để giao diện vẫn hiển thị được.

Create/Edit modal vẫn giữ nguyên UI demo. Nối POST/PUT API thật sẽ thực hiện trong **T016**.

## Thông tin task

- Task ID: T015
- Tên task: Course list page
- Stream: Frontend
- Module: Course
- Priority: P0 - Must
- Dependency: Course API (T014)
- Definition of Done: Xem danh sách môn học trên UI

## Thay đổi chính

### Tích hợp API (cập nhật trong lần này)

- Tạo service layer: `frontend/src/services/courseApi.ts`
  - `fetchCourses()` → `GET /api/v1/courses`
  - `fetchCourseById(id)` → `GET /api/v1/courses/{id}`
  - `mapApiCourse()` – chuyển đổi `CourseResponse` backend → `Course` frontend
  - Base URL lấy từ `import.meta.env.VITE_API_URL || 'http://localhost:8000'`

- Cập nhật `frontend/src/pages/Courses.tsx`
  - Bỏ đọc `localStorage` làm nguồn chính
  - Gọi `fetchCourses()` khi load trang
  - Nếu API thành công → hiển thị dữ liệu thật
  - Nếu API lỗi / backend chưa chạy → fallback về mock data
  - Modal create/edit giữ nguyên UI, cập nhật local state (không gọi API – chờ T016)

- Cập nhật `frontend/src/pages/CourseDetail.tsx`
  - Gọi `fetchCourseById(id)` khi vào `/courses/:id`
  - Nếu API trả 404 → hiển thị "Không tìm thấy môn học"
  - Nếu API lỗi khác → fallback về mock data theo id
  - Modal edit giữ nguyên UI, cập nhật local state (không gọi PUT – chờ T016)

### Giao diện (từ lần trước)

- Thêm trang danh sách môn học: `Courses.tsx` / `Courses.css`
- Thêm trang chi tiết môn học: `CourseDetail.tsx` / `CourseDetail.css`
- Gắn route `/courses` và `/courses/:id`
- Cập nhật sidebar navigation

## Chức năng đã có

- Hiển thị danh sách môn học từ **Course API thật** (nếu backend chạy)
- Fallback tự động về mock data (nếu backend chưa chạy)
- Tìm kiếm theo mã môn, tên môn, mô tả
- Grid view / List view
- Xem chi tiết môn học qua `/courses/:id`
- Trạng thái loading, empty state, not found

## Field vẫn dùng placeholder (backend chưa có)

| Field | Lý do | Kế hoạch |
|---|---|---|
| `materialsCount` | Backend T014 chưa có | Sẽ lấy từ Material API |
| `questionsCount` | Backend T014 chưa có | Sẽ lấy từ Question Bank API |
| `instructor` | Backend T014 chưa có | Sẽ bổ sung khi có user profile |
| `semester` | Backend T014 chưa có | Sẽ bổ sung khi có semester model |

Các field này được gán giá trị từ `MOCK_EXTRAS` (nếu id trùng với mock) hoặc placeholder chung `"Giảng viên phụ trách"` / `"Học kỳ hiện tại"`.

## Phần chờ hoàn thiện

| Task | Nội dung |
|---|---|
| T016 | Nối Create/Edit modal với `POST /api/v1/courses` và `PUT /api/v1/courses/{id}` |
| T010/T011 | Auth/JWT/RBAC thật – thay mock `current_user_id = 1, role = "admin"` |
| Material API | Lấy `materialsCount` thật theo course |
| Question API | Lấy `questionsCount` thật theo course |

## Cách hoạt động

### Khi backend chạy

```
GET http://localhost:8000/api/v1/courses
→ Hiển thị dữ liệu thật từ PostgreSQL
```

```
GET http://localhost:8000/api/v1/courses/{id}
→ Hiển thị chi tiết môn học thật
```

### Khi backend chưa chạy

Trang vẫn hiển thị mock data. Console sẽ in:
```
[T015] fetchCourses failed, using mock data: ...
```

## Kiểm tra đã chạy

```bash
npm.cmd run lint   # Không báo lỗi
npm.cmd run build  # Build thành công
```

## Ghi chú

- Axios timeout 8 giây cho mỗi request để tránh treo UI khi backend chậm.
- Request cleanup qua `cancelled` flag để tránh setState sau khi component unmount.
- Backend hiện mock `current_user_id = 1` và `role = "admin"` nên không cần token khi gọi API ở môi trường dev.
