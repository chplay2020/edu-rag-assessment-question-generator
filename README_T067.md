# T067: Job progress UI

## Mục tiêu (Goal)
Hiển thị tiến trình xử lý tài liệu/sinh câu hỏi trên giao diện (Frontend), giúp người dùng biết được quá trình đang diễn ra (Processing, Failed, Done) một cách trực quan, tận dụng các trường dữ liệu `percent` và `started_at` vừa được thêm từ Task T066.

## Chi tiết thay đổi (Changes)
1. **Cập nhật Types / Interfaces:**
   - Trong `frontend/src/services/materialApi.ts` và `frontend/src/services/jobApi.ts`: Bổ sung các trường `percent`, `started_at`, `error_message` vào interface `JobResponse` để TypeScript hiểu đúng kiểu dữ liệu.

2. **Cập nhật giao diện chi tiết tài liệu (`MaterialDetail.tsx`):**
   - Bổ sung state `jobPercent` để lưu % hoàn thành khi polling API trạng thái Job.
   - Hiển thị trực quan `%` ngay trên nút "Đang xử lý" (ví dụ: *Đang xử lý (45%)*) để người dùng dễ theo dõi tiến độ phân tích và bóc tách nội dung PDF/Docx.

3. **Cập nhật giao diện kết quả tạo câu hỏi (`JobResult.tsx`):**
   - Bổ sung phần trăm tiến độ sinh câu hỏi vào tiêu đề đang tải (ví dụ: *Đang sinh câu hỏi (70%)*).
   - Hiển thị thời gian bắt đầu chạy Job (format: `Bắt đầu lúc: HH:MM:SS`) nếu `started_at` có dữ liệu, giúp người dùng ước lượng được hệ thống đã mất bao lâu.

4. **Khắc phục lỗi cache (Vite):**
   - Chạy lệnh restart lại container frontend để xóa bộ nhớ đệm ẩn của Vite, tránh lỗi màn hình trắng hay lỗi HMR trên môi trường Docker Windows.

## Kiểm thử (Testing)
- Chạy lệnh biên dịch TypeScript (tsc) không có lỗi (0 errors).
- Trạng thái polling cập nhật thành công `%` theo thời gian thực thay vì chỉ quay tròn vô định.

