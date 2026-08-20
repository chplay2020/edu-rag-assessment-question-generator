# Task T061: Export Excel Service

## Mục tiêu
Triển khai service xuất file Excel cho các câu hỏi từ ngân hàng câu hỏi (Question Bank) sử dụng thư viện `openpyxl`. Tính năng này cung cấp file `.xlsx` cho người dùng tải xuống, chứa đầy đủ thông tin về nội dung câu hỏi, độ khó, Bloom, giải thích và các đáp án linh động.

## Các chức năng chính đã triển khai

### 1. Hỗ trợ số lượng Option linh hoạt
- Nếu một batch câu hỏi có nhiều options hơn tiêu chuẩn (ví dụ có 5 options), file Excel sẽ **tự động chèn thêm cột** (VD: "Đáp án E", "Đáp án F").
- Các cột nằm sau danh sách option (như "Đáp án đúng", "Giải thích", "Nguồn") sẽ tự động dời sang các cột tương ứng, không bị ghi đè hay mất dữ liệu.
- Cột "Đáp án đúng" được tính bằng chữ cái (A, B, C, D, E...) dựa theo giá trị `is_correct` của Option.

### 2. Bảo mật - Chống Spreadsheet Formula Injection
- Bất kỳ text nào (kể cả nội dung, option hay giải thích) bắt đầu bằng các ký tự có thể gây thực thi công thức trong Excel như `=`, `+`, `-`, hoặc `@` sẽ tự động được escape bằng dấu nháy đơn `'` ở đầu.
- Ví dụ: Một câu hỏi có nội dung `=1+1` sẽ được xuất ra Excel thành `'=1+1`.

### 3. Tối ưu truy vấn (Eager Loading)
- Dữ liệu `options` và `material` của mỗi `Question` được eager loading ngay trong truy vấn chính (sử dụng `joinedload` và `selectinload`) qua tham số `with_relations=True` để ngăn chặn lỗi N+1 Query.

### 4. Logic Lọc và Bảo Mật (Tích hợp từ T059)
- Câu hỏi thuộc trạng thái `draft`, `review_required` hoặc `rejected` sẽ không được phép truy xuất.
- Giảng viên chỉ được phép xuất những câu hỏi được tạo từ tài liệu mà họ quản lý (hoặc Admin).
- Yêu cầu export sẽ thất bại và trả về HTTP 422 Unprocessable Entity kèm theo danh sách `invalid_question_ids` nếu bất kỳ một `question_id` nào không thoả mãn các điều kiện trên.
- Đảm bảo **bảo toàn thứ tự id** mà client gửi lên và loại bỏ các id trùng lặp.

### 5. Giao thức trả về File trực tiếp
- API Endpoint: `POST /api/v1/exports/excel`
- Payload: `{"question_ids": [1, 2, 3]}`
- Response: Trả về file nhị phân qua `StreamingResponse` với `Content-Disposition` attachment (VD: `questions_export_20260820_174000.xlsx`).

## Cách kiểm thử
1. Cài đặt thư viện (Đã cài): `pip install -r requirements.txt` (yêu cầu `openpyxl>=3.1.0`).
2. Chạy test suite: 
   ```bash
   docker compose exec backend python -m pytest tests/test_export.py -v
   ```

Tất cả các unit và integration test đều đã đi qua các kịch bản thực tế nhằm bảo đảm tính chính xác và an toàn của module.
