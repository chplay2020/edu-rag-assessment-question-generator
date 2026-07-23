# README T020 – Material Upload Page (Frontend)

## Tổng quan

Task T020 triển khai giao diện tải lên và quản lý tài liệu học tập cho giảng viên/admin, tích hợp với backend T019 đã hoàn thành.

---

## Chức năng đã làm

### 1. Service API (`frontend/src/services/materialApi.ts`)
- **Type `Material`**: `id`, `title`, `course_id`, `uploaded_by`, `file_url`, `status`, `created_at`
- **`uploadMaterial(courseId, file)`**: Gửi `multipart/form-data` gồm `course_id` và `file` — không set `Content-Type` thủ công, để axios tự xử lý boundary
- **`getMaterialsByCourse(courseId)`**: Lấy danh sách tài liệu theo môn học
- **`validateFile(file)`**: Validate định dạng và kích thước ở frontend
- **`extractApiError(err)`**: Chuẩn hóa lỗi API thành thông báo tiếng Việt
- **`formatViDate(isoString)`**: Format ngày giờ tiếng Việt
- **`formatFileSize(bytes)`**: Format dung lượng file

### 2. Trang quản lý tài liệu (`/courses/:id/materials`)
- Route: `/courses/:id/materials` (protected, trong `MainLayout`)
- Component: `frontend/src/pages/CourseMaterials.tsx`
- CSS: `frontend/src/pages/CourseMaterials.css`
- Sử dụng thanh điều hướng Breadcrumb (`Môn học / [Tên môn học] / Tài liệu`) dùng chung từ `index.css`.
- Hiển thị mã và tên môn học từ Course API

### 3. Khu vực upload
- Vùng kéo-thả + click để chọn file
- Sử dụng Custom Image Icon (`/upload_icon.png`)
- Hiển thị rõ: "PDF, DOCX hoặc TXT · tối đa 10 MB"
- Sau khi chọn file: tên file + dung lượng + nút bỏ chọn
- Nút "Tải lên tài liệu" chỉ enabled khi file hợp lệ đã được chọn
- Trạng thái uploading: disable vùng chọn + nút "Đang tải lên..." + spinner
- Thành công: toast xanh + reset file + reload danh sách
- Lỗi: toast đỏ + inline error message + cho phép thử lại

### 4. Validate frontend
- Chặn file không phải PDF/DOCX/TXT (check cả MIME type và extension)
- Chặn file > 10 MB
- Hiển thị thông báo lỗi rõ ràng ngay bên dưới vùng chọn

### 5. Danh sách tài liệu
- Gọi `GET /api/v1/materials/course/{course_id}` khi vào trang
- Loading spinner, error state (có nút "Thử lại"), empty state
- Mỗi item: tên tài liệu, status badge, thời gian upload (tiếng Việt), nút "Tải xuống"
- Nút tải xuống mở `file_url` trong tab mới

### 6. Cập nhật CourseDetail
- Panel "Tài liệu học tập": bỏ placeholder text
- Header & Breadcrumb: Được chuẩn hóa UI/UX đồng bộ với trang quản lý tài liệu.
- Nút "Quản lý tài liệu" → `/courses/:id/materials` (có hover effect)
- Số tài liệu thật từ `getMaterialsByCourse` (hiện `—` khi đang fetch hoặc lỗi)

---

## API tích hợp

| Phương thức | Endpoint | Mục đích |
|---|---|---|
| `POST` | `/api/v1/materials/upload` | Upload tài liệu (`multipart/form-data`: `course_id` + `file`) |
| `GET` | `/api/v1/materials/course/{course_id}` | Lấy danh sách tài liệu |

- Bearer token: tự động từ `apiClient` trong `courseApi.ts` (interceptor đọc `localStorage.access_token`)
- Base URL: `VITE_API_URL` hoặc `http://localhost:8000/api/v1`

---

## Định dạng và giới hạn file

| Định dạng | MIME Type | Extension |
|---|---|---|
| PDF | `application/pdf` | `.pdf` |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `.docx` |
| TXT | `text/plain` | `.txt` |

- Giới hạn: **10 MB**
- Validate cả MIME type lẫn extension (để xử lý các trường hợp browser không detect đúng MIME)

---

## Các trạng thái UI

| Trạng thái | Mô tả |
|---|---|
| Idle (chưa chọn file) | Vùng drop zone trống, nút upload disabled |
| File đã chọn | Hiển thị tên + dung lượng, nút enabled |
| File không hợp lệ | Inline error bên dưới drop zone, nút disabled |
| Uploading | Drop zone disabled, nút "Đang tải lên...", spinner |
| Upload thành công | Toast xanh, file reset, danh sách reload |
| Upload thất bại | Toast đỏ + inline error, cho phép thử lại |
| Danh sách đang tải | Spinner loading |
| Danh sách lỗi | Error message + nút "Thử lại" |
| Danh sách rỗng | Empty state với icon và hướng dẫn |

### Status badge tài liệu (Hallmark Minimal Dot Style)
- `processing` → chấm vàng, nhãn `Đang xử lý`
- `pending` → chấm vàng, nhãn `Đang chờ`
- `ready` → chấm xanh "Sẵn sàng"
- `error` → chấm đỏ "Lỗi"

---

## Files đã tạo/sửa

### Tạo mới
- `frontend/src/services/materialApi.ts` — Material API service
- `frontend/src/pages/CourseMaterials.tsx` — Upload + danh sách trang
- `frontend/src/pages/CourseMaterials.css` — Styles

### Chỉnh sửa
- `frontend/src/App.tsx` — Thêm route `/courses/:id/materials`
- `frontend/src/pages/CourseDetail.tsx` — Update panel tài liệu (real count, navigation button)
- `frontend/src/pages/CourseDetail.css` — Thêm style `btn-section-materials-active`

---

## Giới hạn ngoài phạm vi T020

- Xóa tài liệu (chưa có API)
- Preview PDF/DOCX trong browser
- Progress bar upload thật (API chưa hỗ trợ server-sent events)
- Chunking, embedding, AI/RAG
- Phân quyền chi tiết: Frontend chưa có UI hiển thị riêng theo role; quyền owner/admin được backend kiểm soát.
- Pagination danh sách tài liệu
- Sắp xếp/lọc danh sách tài liệu



