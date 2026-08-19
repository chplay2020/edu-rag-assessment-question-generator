# Task T051: Question Status Workflow

## Mô tả
T051 tập trung vào việc quản lý vòng đời (trạng thái) của một câu hỏi trong hệ thống:
- Các trạng thái hợp lệ: `draft` (Nháp), `review_required` (Chờ duyệt), `approved` (Đã duyệt), `rejected` (Từ chối).
- Phân quyền rõ ràng đối với thao tác duyệt câu hỏi.
- Quản lý quá trình chuyển đổi trạng thái (State Transition).

## Các thay đổi chính
- **Cập nhật Backend (`questions.py` & `question.py`)**: 
  - Quy định rõ những trạng thái nào được phép thiết lập khi tạo câu hỏi.
  - Bổ sung logic kiểm soát chuyển đổi trạng thái khi câu hỏi được chỉnh sửa (chuyển câu hỏi từ đã duyệt/bị từ chối về dạng nháp/chờ duyệt).
  - Tích hợp kiểm tra quyền của người dùng (permissions) khi gọi API review.

## Cách kiểm thử
1. Tạo một câu hỏi mới, trạng thái mặc định phải là `draft` hoặc `review_required`.
2. Dùng tài khoản Giảng viên / Reviewer để thực hiện gọi API `/questions/{question_id}/review` để chuyển trạng thái sang `approved` hoặc `rejected`.
3. Kiểm tra không cho phép chuyển trạng thái một cách tùy tiện ngoài các state hợp lệ.
