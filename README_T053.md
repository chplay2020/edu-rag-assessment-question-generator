# Task T053: QuestionReview Log

## Mô tả
T053 xây dựng tính năng theo dõi lịch sử duyệt (Review Log) đối với từng câu hỏi trong hệ thống. Điều này giúp đảm bảo tính minh bạch, xem lại được lý do tại sao một câu hỏi được duyệt (approved) hay bị từ chối (rejected).

## Các thay đổi chính
- **Model `Review` (`review.py`)**: 
  - Lưu lại thông tin người duyệt (`reviewed_by`), thao tác duyệt (`status`: `approved`/`rejected`), lý do hoặc bình luận (`feedback`), và thời gian duyệt (`created_at`).
  - Thiết lập relationship liên kết với bảng `Question` và bảng `User`.
- **API Review (`POST /questions/{question_id}/review`)**:
  - Ghi log hành động duyệt của giảng viên vào bảng `reviews` đồng thời cập nhật lại trạng thái (`status`) của `Question` tương ứng.
- **API History (`GET /questions/{question_id}/reviews`)**:
  - Cung cấp dữ liệu lịch sử các lần duyệt (ai đã duyệt, duyệt lúc nào, nhận xét gì) để hiển thị lên frontend.

## Cách kiểm thử
1. Gọi API review một câu hỏi với trạng thái `rejected`, cung cấp feedback rõ ràng (ví dụ: "Câu hỏi sai kiến thức").
2. Gọi API get history để xem log có ghi nhận đúng thông tin `reviewed_by`, `status`, `feedback` và `created_at` hay không.
3. Review lại lần nữa thành `approved` và kiểm tra lịch sử xem có ghi nhận đủ 2 bản ghi review hay không.
