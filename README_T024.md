# README - T024: Text Cleaning Service

## Mục tiêu
Nhiệm vụ T024 tập trung vào việc làm sạch dữ liệu văn bản thô (raw text) ở T023. Dữ liệu sau khi làm sạch sẽ gọn gàng, đồng nhất, và loại bỏ các thành phần dư thừa như header/footer lặp lại, khoảng trắng thừa, giúp cải thiện chất lượng khi đưa vào mô hình nhúng (embedding) và RAG sau này.

## Phạm vi và Quy tắc làm sạch
- **Khoảng trắng và Dòng trống**:
  - Tự động chuẩn hóa dấu xuống dòng (`\r\n` hoặc `\r` về `\n`).
  - Xóa khoảng trắng ở đầu và cuối mỗi dòng.
  - Gộp các khoảng trắng liên tiếp trong cùng một dòng thành một khoảng trắng duy nhất.
  - Các dòng trống liên tiếp (nhiều hơn 1) sẽ bị thu gọn lại thành tối đa 1 dòng trống (tránh làm rác cơ sở dữ liệu véc-tơ).
- **Phân trang và Ký tự đặc biệt**:
  - Dấu ngắt trang (`\f`) được sử dụng để xác định ranh giới trang, sau đó bị xóa bỏ khỏi văn bản cuối cùng.
- **Header và Footer**:
  - Tự động phát hiện các dòng văn bản lặp lại ở đầu hoặc cuối từ 2 trang trở lên (như tiêu đề giáo trình, chân trang môn học).
  - T024 dùng heuristic đơn giản: chỉ xét dòng ngắn lặp lại ở đầu hoặc cuối từ hai trang trở lên. Kết quả cần được kiểm tra lại với tài liệu thực tế.

## Vị trí lưu trữ Output
Văn bản sau khi làm sạch được lưu trữ qua cơ chế *Atomic Write* (ghi an toàn bằng đuôi `.tmp` trước khi đổi tên) tại:
`storage/processed/material_<id>/clean.txt`
(*Thư mục gốc được lấy từ biến môi trường `PROCESSED_DIR`, mặc định là `storage/processed`*).

## Giới hạn hiện tại
- T024 hoàn toàn chỉ xử lý chuỗi văn bản (String processing) thuần túy.
- Chưa áp dụng Chunking, Embedding, hay RAG.
- Chưa tạo API Endpoint

## Kiểm thử thủ công
- Đọc `storage/processed/material_8/raw.txt`.
- Chạy `clean_and_save(8, raw_text)`.
- Kiểm tra `storage/processed/material_8/clean.txt` vẫn có nội dung tiếng Việt hợp lý và không còn khoảng trắng/dòng trống dư.

## Kiểm thử (Unit Test)
Tất cả kịch bản đều được kiểm thử thành công bằng pytest:
- Tự động gộp khoảng trắng, gộp dòng trống, chuẩn hóa ký tự newline.
- Khử an toàn ký tự form-feed `\f`.
- Thuật toán xóa header/footer hoạt động chính xác với file có nhiều trang lặp lại.
- Dữ liệu không lặp lại vẫn được giữ nguyên vẹn.
- Kiểm tra tính năng lưu ra thư mục `clean.txt`.
