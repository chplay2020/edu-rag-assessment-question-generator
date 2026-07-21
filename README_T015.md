# Báo cáo thay đổi: Task T015 - Course List Page

## Mức độ hoàn thành
Đã hoàn thành trang danh sách môn học và tích hợp dữ liệu thật từ Course API.

## Chức năng đã thực hiện
- Hiển thị danh sách môn học từ `GET /api/v1/courses`.
- Tìm kiếm theo mã, tên môn học.
- Chuyển đến trang chi tiết môn học.
- Có trạng thái đang tải, chưa có môn học và lỗi tải dữ liệu.
- Nếu API trả `401`, tự xóa token và chuyển về trang đăng nhập.
- Không sử dụng dữ liệu môn học mock làm dữ liệu dự phòng.

## Phụ thuộc
- Course API: T014.
- Xác thực JWT: T010/T011.

## Kiểm thử
- Đăng nhập thành công.
- Danh sách hiển thị dữ liệu từ PostgreSQL.
- Tìm kiếm hoạt động.
- Không có môn học hiển thị trạng thái hướng dẫn tạo môn học.
- Token hết hạn hoặc không hợp lệ sẽ quay về trang đăng nhập.