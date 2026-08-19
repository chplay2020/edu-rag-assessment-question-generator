# Task T055: Question Editor Modal/Form

## Mô tả
T055 triển khai một Modal hoặc Biểu mẫu (Form) UI để chỉnh sửa chi tiết của một câu hỏi ngay trên Frontend. Đây là tính năng cốt lõi cho phép Reviewer can thiệp và sửa đổi nội dung do AI sinh ra nếu chưa đạt yêu cầu.

## Các chức năng chính
- **Form chỉnh sửa**: Cung cấp các trường nhập liệu tương ứng:
  - Textarea cho **Nội dung câu hỏi (Question Text)** và **Giải thích (Explanation)**.
  - Dropdown cho **Độ khó (Difficulty)** và **Mức độ nhận thức (Bloom Level)**.
- **Quản lý đáp án (Options Manager)**:
  - Cho phép sửa Text của từng đáp án.
  - Radio button / Checkbox để đánh dấu đáp án đúng (`is_correct`).
  - Nút thêm/xóa đáp án linh hoạt.
- **Lưu dữ liệu**: Form gọi API `PUT /questions/{question_id}` đã được định nghĩa ở T052 để lưu thay đổi về Backend. Nếu lưu thành công, pop-up tự đóng và danh sách câu hỏi cập nhật.

## Mục tiêu trải nghiệm
- Trải nghiệm mượt mà, không cần tải lại cả trang khi sửa câu hỏi.
- Giao diện trực quan, rõ ràng cho việc soạn thảo đáp án trắc nghiệm.
