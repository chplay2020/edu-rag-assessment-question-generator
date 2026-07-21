# Báo cáo thay đổi: Task T016 - Course Create/Edit Form

## Mức độ hoàn thành
Đã hoàn thành giao diện tạo và chỉnh sửa môn học, tích hợp với Course API thật.

## Chức năng đã thực hiện
- Form tạo môn học gọi `POST /api/v1/courses`.
- Form chỉnh sửa môn học gọi `PUT /api/v1/courses/{course_id}`.
- Form chỉ gửi các trường backend hỗ trợ: `code`, `title`, `description`.
- Không cho người dùng tự chọn giảng viên phụ trách; người tạo môn học được backend xác định từ JWT.
- Kiểm tra bắt buộc cho mã môn học, tên môn học và mô tả.
- Báo lỗi rõ khi mã môn học đã tồn tại.
- Sau khi tạo hoặc sửa thành công, danh sách môn học được cập nhật ngay trên giao diện.
- Hiển thị lỗi API khi tạo hoặc cập nhật thất bại.

## Phụ thuộc
- Course API: T014.
- JWT và phân quyền: T010/T011.
- Trang danh sách môn học: T015.

## Kiểm thử
- Lecturer đăng nhập và tạo môn học thành công.
- Tạo môn học trùng mã hiển thị thông báo lỗi.
- Chỉnh sửa tên, mã hoặc mô tả môn học thành công.
- Dữ liệu mới hiển thị lại trong danh sách và trang chi tiết.
- Không có token hoặc token hết hạn sẽ quay về trang đăng nhập.