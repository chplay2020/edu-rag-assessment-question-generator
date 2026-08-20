# Task T056: Approve/Reject Actions

## Mô tả
T056 tích hợp các hành động duyệt (Approve) và từ chối (Reject) vào giao diện để hoàn thiện quy trình Review Question (tương ứng với API T053 Backend).

## Các chức năng chính
- **Nút tương tác (Action Buttons)**: 
  - Nút **Approve** (Màu xanh, tick).
  - Nút **Reject** (Màu đỏ, chéo).
- **Confirm & Comment Modal**:
  - Khi người dùng bấm **Reject**, UI sẽ bật lên một hộp thoại nhỏ (Modal) yêu cầu (hoặc khuyến khích) nhập lý do/nhận xét (Comment/Feedback) trước khi xác nhận.
  - Khi bấm **Approve**, người dùng cũng có thể nhập feedback tùy chọn (optional) hoặc duyệt nhanh (Quick Approve).
- Tích hợp với API `POST /questions/{question_id}/review`.

## Mục tiêu trải nghiệm
- Thao tác nhanh chóng, tiết kiệm thời gian cho Reviewer khi duyệt nhiều câu hỏi liên tục.
- Đảm bảo tính cẩn trọng (confirm) để tránh bấm nhầm làm thay đổi trạng thái câu hỏi sai ý muốn.
