# Task T052: Question Edit API

## Mô tả
T052 cung cấp API cho phép người dùng chỉnh sửa nội dung chi tiết của một câu hỏi đã tạo. API này hỗ trợ việc cập nhật các trường liên quan đến nội dung cũng như thiết lập các đáp án.

## Các thay đổi chính
- **API `PUT /questions/{question_id}`**:
  - Hỗ trợ cập nhật các trường: `content`, `difficulty`, `bloom_level`, `question_type`, `explanation`, `source_chunk_ids`.
  - Hỗ trợ cập nhật lại danh sách đáp án (`options`): cho phép xóa danh sách cũ và cập nhật danh sách mới, chỉ định đáp án đúng (`is_correct`).
- **Validation**: Tự động gọi hàm `revalidate_question` để kiểm tra tính hợp lệ của câu hỏi (ví dụ: độ dài, định dạng, ...).
- **Workflow Interceptor**: Cấu hình logic khi một câu hỏi bị chỉnh sửa, nó sẽ mất đi trạng thái `approved` (đã duyệt) để yêu cầu duyệt lại, đảm bảo tính nhất quán dữ liệu.

## Cách kiểm thử
1. Lấy ID của một câu hỏi tồn tại.
2. Gọi API `PUT /questions/{question_id}` truyền vào body mới chứa nội dung, danh sách đáp án đã thay đổi.
3. Kiểm tra xem các thay đổi đã được lưu trong DB hay chưa, đặc biệt là đáp án cũ đã bị xóa và thay bằng đáp án mới.
4. Kiểm tra trạng thái duyệt (`status`) của câu hỏi sau khi chỉnh sửa có trở về `draft` / `review_required` hay không.
