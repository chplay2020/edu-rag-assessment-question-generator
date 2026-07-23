# T022 - Material List/Detail UI

## Mục tiêu
Triển khai giao diện chi tiết tài liệu (Material Detail) cho phép người dùng xem thông tin metadata, tải file, xem trước nội dung trích xuất, và chuẩn bị nút chức năng "Xử lý tài liệu" (hiện đang disabled, chờ T028/T029). Đảm bảo giữ nguyên các chức năng upload/list hiện có của T020.

## Danh sách file đã tạo hoặc chỉnh sửa
- **Sửa:** `frontend/src/services/materialApi.ts` (Thêm interface `MaterialDetail`, hàm `getMaterialById`, và helper `downloadMaterialFile`).
- **Sửa:** `frontend/src/pages/CourseMaterials.tsx` & `.css` (Sử dụng helper download, thêm liên kết sang trang chi tiết bằng `<Link>`).
- **Sửa:** `frontend/src/App.tsx` (Thêm route mới).
- **Tạo mới:** `frontend/src/pages/MaterialDetail.tsx` & `frontend/src/pages/MaterialDetail.css` (Giao diện chi tiết tài liệu).
- **Tạo mới:** `README_T022.md`.

## API được sử dụng
- `GET /api/v1/materials/{material_id}`: Lấy chi tiết tài liệu.
- `GET /api/v1/courses/{course_id}`: Lấy thông tin khóa học (phục vụ breadcrumb và metadata).

## Route frontend mới
- `/courses/:courseId/materials/:materialId`: Trang chi tiết tài liệu.

## Các trường hiển thị trên trang chi tiết
- Tên tài liệu và icon (dựa trên đuôi file).
- Metadata: Mã môn học, Tên môn học, Trạng thái xử lý, Ngày tải lên, ID người tải (`uploaded_by`), Số đoạn nội dung (`chunk_count`).
- Vùng Xem trước nội dung (`extracted_text_preview`).

## Mapping trạng thái
- `processing` / `pending` → Đang xử lý
- `done` / `completed` / `ready` → Đã xử lý (Sẵn sàng)
- `error` / `failed` → Xử lý thất bại
- Các trạng thái khác → Chưa xác định

## Loading, Error & Empty state
- **Loading:** Hiển thị spinner ở giữa màn hình trong lúc fetch dữ liệu.
- **Error (404/403, sai ID):** Hiển thị màn hình báo lỗi với thông điệp: "Không tìm thấy tài liệu hoặc bạn không có quyền truy cập." và có nút quay lại.
- **Kiểm tra courseId hợp lệ:** Đảm bảo `material.course_id === courseId` lấy từ URL; nếu sai sẽ chặn không cho xem và hiển thị màn hình lỗi.
- **Empty Preview:** Nếu `extracted_text_preview` là null hoặc rỗng, hiển thị box có icon và dòng chữ thông báo "Chưa có nội dung trích xuất. Nội dung sẽ xuất hiện sau khi tài liệu được xử lý."

## Chú ý (Phụ thuộc vào Task tương lai)
- **Nút "Xử lý tài liệu"** hiện tại luôn được hiển thị nhưng ở trạng thái `disabled`. Logic gọi Process API thực tế và cơ chế polling thuộc về phạm vi của **T028** (Backend Process API) và **T029** (Frontend Polling/Status), không phải của T022.

## Hướng dẫn kiểm thử thủ công
1. Đăng nhập bằng tài khoản lecturer.
2. Vào màn hình chi tiết một course, chọn qua tab tài liệu hoặc click vào danh sách tài liệu.
3. Click vào Tên tài liệu hoặc nút "Xem chi tiết". Trình duyệt sẽ chuyển hướng sang URL dạng `/courses/1/materials/5`.
4. Quan sát thông tin metadata hiển thị đầy đủ, breadcrumb hiển thị đúng đường dẫn.
5. Kiểm tra preview nội dung (nếu tài liệu chưa xử lý sẽ hiển thị Empty state báo chưa có).
6. Click vào nút "Tải xuống" để kiểm tra tính năng tải file.
7. Di chuột qua nút "Xử lý tài liệu", nút phải hiển thị tooltip giải thích và không click được.
8. Thử sửa URL courseId thành một ID khác, trang sẽ hiển thị lỗi 404 bảo mật truy cập chéo.
9. Kiểm tra responsive bằng việc thu nhỏ trình duyệt xuống dạng mobile.
10. Kiểm tra thêm các trường hợp URL có `courseId` hoặc `materialId` không hợp lệ (không phải số nguyên dương như `abc`, `1.5`, `-1`): Trang phải hiển thị lỗi, không gọi API, và nút quay lại dẫn về `/courses` thay vì tạo URL lỗi `/courses/NaN/materials`.

## Kết quả kiểm tra
- `npm run lint`: 0 error. Còn 2 warning `exhaustive-deps` có sẵn tại `Courses.tsx` và `CourseDetail.tsx`, không phát sinh từ T022.
- `npm run build`: Build thành công. Cảnh báo bundle lớn hơn 500 kB là cảnh báo có sẵn, không chặn T022.
- `git diff --check`: Không có lỗi khoảng trắng (whitespace error).
