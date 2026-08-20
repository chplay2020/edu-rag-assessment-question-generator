# Task T062 & T063: Lịch sử Export (Backend) & Xuất Excel (Frontend)

## 1. Task T062: Export History API (Backend)

### Mục tiêu
Theo dõi và lưu trữ lịch sử tải file Excel của người dùng, đảm bảo tính nguyên vẹn dữ liệu, khả năng khôi phục hoặc xem lại, cũng như bảo mật đường dẫn trên server. Tính năng được mở rộng dựa trên lõi xuất file của T061.

### Các chức năng chính đã triển khai
- **Cấu trúc Database (Model & Migration)**: Thêm model `Export` liên kết với bảng `users`. Thông tin lưu trữ bao gồm `file_name` (chỉ lưu tên file an toàn, tuyệt đối không lưu đường dẫn tuyệt đối), `course_id` (có thể null nếu export nhiều môn), `question_ids` (chuỗi JSON chứa mảng ID), kích thước file và thời gian xuất.
- **Service & Persistence Logic**:
  - Ghi nhận lịch sử `Export` xuống Database **sau khi** file Excel đã được tạo thành công trên hệ thống file local.
  - Xử lý lỗi toàn diện (Transaction Rollback): Nếu quá trình lưu thông tin xuống database thất bại, file Excel vừa được ghi trên đĩa cũng sẽ được dọn dẹp (cleanup) để tránh rác.
- **Bảo mật thư mục (Path Traversal Prevention)**: Tại API `GET /exports/{id}/download`, sử dụng cơ chế bảo vệ an toàn để bắt buộc file chỉ được đọc từ đúng thư mục chỉ định (`storage/exports`), không cho phép các chuỗi can thiệp kiểu `../../`.
- **API Endpoints**:
  - Tích hợp ghi lịch sử vào: `POST /api/v1/exports/excel`.
  - API Lịch sử: `GET /api/v1/exports`.
  - API Tải lại file: `GET /api/v1/exports/{id}/download`.

---

## 2. Task T063: Export Excel (Frontend)

### Mục tiêu
Tích hợp quy trình chọn câu hỏi từ Ngân hàng câu hỏi (Question Bank) và gửi xuống Server để lấy file Excel. Yêu cầu tải file an toàn, chặn click rác và xử lý thông minh các lỗi nghiệp vụ.

### Các chức năng chính đã triển khai
- **Xử lý Tải File an toàn (Blob Download & Cleanup)**: 
  - Khởi tạo Blob lấy từ server (qua tuỳ chọn `responseType: 'blob'`). 
  - Bọc URL ảo (ObjectURL) và thẻ anchor `<a>` vào khối `try/finally` chặt chẽ. Xoá URL ảo và anchor khỏi DOM ngay lập tức sau khi click tải về để chặn rò rỉ RAM (memory leak).
  - Khống chế MIME Type: Từ chối tải và hiển thị ngay cảnh báo nếu Server vô tình trả JSON hoặc Text (đội lốt 200 OK) thay vì file thực.
- **Filename Parser (CORS)**: 
  - Đọc tên file chuẩn chỉnh từ Backend nhờ việc bổ sung lệnh `expose_headers=["Content-Disposition"]` ở API backend (`main.py`).
  - Hỗ trợ parser 2 tầng ưu tiên: Tầng 1 dịch mã decode `filename*=UTF-8''`, Tầng 2 dịch mã `filename="..."`.
  - Tự động sinh `questions_export_YYYYMMDD_HHMMSS.xlsx` nếu không lấy được header từ server.
- **Khống chế Giao diện (Double-click Guard)**:
  - Khóa đồng bộ (`exportInFlightRef` kết hợp `isExporting` state) chặn cứng hiện tượng người dùng spam click nhiều lần gửi hàng loạt request. Nút bấm biến đổi hiển thị icon tải (Spin) trong suốt quá trình xử lý.
- **Xử lý Lỗi thông minh (Error Formatter)**: 
  - Dù gọi request dạng file (Blob), khi server quăng lỗi 422 hay 500, Frontend tự động "bóc" Blob thành Text và parse ngược về JSON để lấy được lỗi cụ thể (như "Câu hỏi không hợp lệ"). Điều này triệt tiêu hoàn toàn sự cố giao diện hiện chữ `[object Blob]` ác mộng.

### Cách kiểm thử (T063)
1. Cài đặt các modules: `npm install` (trong thư mục `frontend`).
2. Run Type Check / Linter: `npm run lint`.
3. Kiểm tra Build an toàn: `npm run build`.
4. Mở trình duyệt, vào trang Ngân hàng câu hỏi, chọn 1 hoặc nhiều câu hỏi và bấm **Xuất Excel**.
