# Hoàn thành các Task T037, T038

Các thay đổi sau đã được thực hiện để hoàn thành các chức năng giao diện (Frontend) cho việc sinh và xem kết quả câu hỏi.

## T037: Question generation form
- **API Integration**: Đã tạo file `frontend/src/services/jobApi.ts` để kết nối với các API tạo job sinh câu hỏi (`POST /jobs/material/{id}/generate-questions`).
- **Giao diện Form (`GenerateQuestions.tsx`)**: Đã thiết kế giao diện form chuyên dụng để cho phép giảng viên nhập các thông số sinh câu hỏi:
  - Chọn số lượng câu hỏi (mặc định 5, tối đa 50).
  - Chọn độ khó (Dễ, Trung bình, Khó).
  - Chọn mức độ nhận thức Bloom (Tất cả, Nhớ, Hiểu, Vận dụng, Phân tích, Đánh giá, Sáng tạo).
  - Chọn ngôn ngữ (Tiếng Việt, Tiếng Anh).
  - Khung text để nhập thêm yêu cầu tùy chỉnh (Từ khóa, chỉ sinh vào một chương cụ thể...).
- **Flow**: Nút "Tạo câu hỏi" trong trang Chi tiết tài liệu (`MaterialDetail.tsx`) đã được làm sáng lên khi trạng thái tài liệu là đã xử lý xong. Khi bấm vào sẽ điều hướng đến form. Form được validate và gửi dữ liệu lên Backend để khởi tạo tiến trình nền (Background Job).

## T038: Generated questions result page
- **Trang Kết quả (`JobResult.tsx`)**: Đã tạo trang hiển thị trạng thái và kết quả sinh câu hỏi:
  - **Auto-polling**: Giao diện liên tục gọi API `GET /jobs/{id}` định kỳ 3 giây để kiểm tra khi tiến trình hoàn tất. Trong thời gian này, màn hình hiển thị trạng thái đang xử lý để người dùng biết.
  - **Render Danh sách Câu hỏi**: Khi trạng thái xử lý xong (`done`), ứng dụng gọi API lấy câu hỏi và vẽ giao diện hiển thị.
  - Mỗi câu hỏi hiển thị đầy đủ:
    - Metadata: Độ khó, mức độ Bloom tương ứng (dưới dạng Badge trực quan).
    - Các lựa chọn đáp án: Lựa chọn đúng được tô màu xanh nổi bật và có icon check (`is_correct`).
    - Nguồn dữ liệu (Source Chunks).
    - Lời giải thích chuyên sâu (Explanation) được hiển thị nổi bật với khối màu vàng nhạt.
- **Tính nhất quán (Consistent CSS)**: Giao diện hoàn toàn đồng bộ với các trang khác qua các class CSS kế thừa (dùng `card-panel`, font chuẩn, bảng màu chủ đạo...).
- **Cập nhật Routing**: Đã tích hợp thành công 2 Route mới vào layout chính thức của ứng dụng thông qua `frontend/src/App.tsx`.
