# README - T023: PDF/TXT Text Extraction Service

## Mục tiêu
Nhiệm vụ T023 tập trung vào việc trích xuất raw text từ các tài liệu PDF (text-based) và TXT. File này thuộc tiến trình xử lý tài liệu, nhưng đứng độc lập như một service. Service này không chứa API endpoint, không làm thay đổi trạng thái Material thành `done` hay `failed`, và không dọn dẹp văn bản (clean text) hay chia nhỏ (chunking).

## Phạm vi hỗ trợ
- **Định dạng hỗ trợ**:
  - `PDF (text-based)`: Trích xuất các trang, giữ nguyên dấu phân tách trang (`\n\f\n`).
  - `TXT`: Hỗ trợ mã hóa utf-8-sig, utf-8, và cp1258.
- **Không hỗ trợ**:
  - Các tệp tin dạng `DOCX` không nằm trong phạm vi xử lý hiện tại.
  - Các PDF chứa hình ảnh hoặc PDF scan (không sử dụng OCR trong giai đoạn này).

## Vị trí lưu trữ Raw Text
Kết quả văn bản thô (raw text) được ghi dưới dạng atomic (tránh việc lỗi lưu nửa chừng) tại thư mục xử lý:
`storage/processed/material_<id>/raw.txt`
(*Lưu ý: thư mục được lấy từ biến môi trường `PROCESSED_DIR`, mặc định là `storage/processed`*).

## Kết quả kiểm tra (Unit Test)
Đã triển khai unit test với `pytest`, kiểm tra các chức năng:
- Trích xuất TXT UTF-8 có chứa nội dung tiếng Việt.
- Trích xuất TXT có UTF-8 BOM.
- Trích xuất PDF text-based cơ bản.
- Trích xuất PDF nhiều trang, bảo đảm việc phân trang qua ký tự `\f`.
- Ném ra ngoại lệ `TextExtractionError` cho PDF trắng hoặc không chứa đoạn text hợp lệ.
- Ném ngoại lệ khi truyền đường dẫn file không tồn tại.
- Ném ngoại lệ khi truyền file có định dạng không được hỗ trợ (DOCX, MP4, v.v.).
- Chức năng lưu (`save_raw_text`) hoạt động đúng thiết kế, lưu tại thư mục cấu hình.
- File upload gốc không bị thay đổi.
