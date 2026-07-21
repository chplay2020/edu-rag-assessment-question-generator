# Báo cáo thay đổi Code: Task T018 (Postman Collection)

## 1. Mức độ hoàn thành
**Task T018 đã hoàn thành 100%.**
- Đã tạo ra file Postman Collection chứa sẵn các kịch bản test (Happy paths & Error cases) cho 2 module lớn nhất hiện tại: **Auth** và **Courses**.
- Collection này được thiết kế để tự động hóa: Khi chạy request Login thành công, nó sẽ tự động lấy `access_token` nhét vào biến môi trường (Environment Variable) để các request sau (Create Course, Get Course) có thể dùng ngay lập tức mà không cần copy-paste thủ công.

## 2. Các API được bao gồm trong Collection

### Thư mục 1: Authentication (Xác thực)
1. **Register (Happy Case):** Đăng ký tài khoản. *Kỳ vọng: 200 OK hoặc 400 Bad Request (nếu trùng email).*
2. **Login - Admin (Happy Case):** Đăng nhập với tài khoản Admin (`admin@gmail.com`). *Kỳ vọng: 200 OK (Tự động lưu Token).*
3. **Login (Error - Wrong Password):** Test nhập sai mật khẩu. *Kỳ vọng: 401 Unauthorized.*
4. **Get Me:** Lấy thông tin user đang đăng nhập. *Kỳ vọng: 200 OK.*

### Thư mục 2: Courses (Khóa học)
*(Các API này sẽ tự động gắn Bearer Token đã lấy được từ bước Login Admin)*
1. **Create Course (Happy Case):** Tạo khóa học mới. *Kỳ vọng: 201 Created (Tự động lưu `course_id` vừa tạo).*
2. **Get All Courses:** Lấy danh sách toàn bộ khóa học. *Kỳ vọng: 200 OK.*
3. **Get Course By ID:** Lấy thông tin chi tiết một khóa học cụ thể. *Kỳ vọng: 200 OK.*
4. **Update Course:** Chỉnh sửa thông tin khóa học. *Kỳ vọng: 200 OK.*
5. **Delete Course:** Xóa mềm khóa học. *Kỳ vọng: 200 OK.*

## 3. Cách sử dụng (Import vào Postman)
1. Mở phần mềm Postman trên máy của bạn.
2. Bấm nút **Import** (hoặc nhấn `Ctrl + O`).
3. Kéo thả file `docs/EduRAG_Postman_Collection.json` vào cửa sổ Import.
4. Một Collection tên là **"Edu RAG API - Auth & Courses"** sẽ xuất hiện.
5. Chạy API **"Login - Admin"** trước tiên để hệ thống tự động lưu Token. Sau đó bạn có thể chạy thoải mái các API còn lại bằng nút "Send" hoặc bấm "Run Collection" để chạy tự động toàn bộ.

## 4. File kịch bản sinh tự động
Nếu API có sự thay đổi sau này, bạn có thể sinh lại file JSON tự động bằng cách chạy script:
```bash
python scripts/generate_postman_collection.py
```
