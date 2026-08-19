# Task T054: Review Dashboard Page

## Mô tả
T054 nhằm mục đích xây dựng một giao diện Dashboard trực quan ở phía Frontend để Giảng viên (Reviewers) có thể dễ dàng quản lý và xem toàn bộ các câu hỏi được AI sinh ra. 

## Các chức năng chính
- **Danh sách câu hỏi**: Hiển thị danh sách các câu hỏi theo dạng List hoặc thẻ (Cards) với thông tin vắn tắt (Nội dung, loại câu hỏi, mức độ Bloom).
- **Hệ thống bộ lọc (Filters)**:
  - Lọc theo **Khóa học (Course)** hoặc **Tài liệu (Material/Job)**.
  - Lọc theo **Trạng thái (Status)**: `draft`, `review_required`, `approved`, `rejected`.
  - Lọc các câu hỏi có **Cảnh báo (Warning)** từ Validation Service (ví dụ: câu hỏi quá ngắn, các lựa chọn đáp án tương tự nhau).
- Tích hợp với các API list/search câu hỏi từ Backend.

## Mục tiêu trải nghiệm
- Giúp Giảng viên theo dõi nhanh chóng khối lượng câu hỏi đang cần duyệt.
- Dễ dàng lọc ra những câu hỏi có vấn đề để xử lý trước.
