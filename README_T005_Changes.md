# Báo cáo Thay đổi Code: Task T005 (Thiết kế ERD & Migration)

File README này tóm tắt những thay đổi trong đợt commit hiện tại để Leader dễ dàng xem xét (Review).

## 1. Mức độ hoàn thành

**Task T005 đã hoàn thành 100%.**

- Đã thiết kế cấu trúc Database (ERD) và ánh xạ thành code Python (Models).
- Đã cấu hình bộ công cụ Alembic.
- Đạt Definition of Done (DoD): Chạy migration thành công không lỗi trên Database rỗng.

## 2. Các phần đã thay đổi trong code

### A. Thêm các Models (Bảng dữ liệu)

Tạo mới các file trong thư mục `backend/app/models/` để định nghĩa 10 bảng (tables) theo yêu cầu:

1. `user.py`: Bảng **User** (Quản lý giảng viên/admin).
2. `course.py`: Bảng **Course** (Quản lý môn học).
3. `material.py`: Bảng **Material**, **Chunk**, **Job** (Quản lý học liệu, đoạn văn bản chia nhỏ, và tiến trình chạy AI).
4. `question.py`: Bảng **Question**, **Option**, **Review** (Ngân hàng câu hỏi, các đáp án, và lịch sử đánh giá của giảng viên).
5. `system.py`: Bảng **Export**, **AiLog** (Lịch sử xuất file và log tiêu thụ token của AI).
6. `__init__.py`: Import tập trung tất cả các bảng.

_Lý do thay đổi_: Tách thành các module riêng biệt giúp code dễ quản lý và dễ tìm kiếm thay vì nhồi nhét tất cả 10 bảng vào 1 file duy nhất. Đã thiết lập đầy đủ Khóa ngoại (Foreign Key) và quy tắc xóa theo tầng (Cascade Delete).

### B. Cấu hình kết nối Cơ sở dữ liệu (Database)

- Sửa `backend/app/core/config.py`: Thêm các thông số kết nối PostgreSQL (`POSTGRES_USER`, `POSTGRES_DB`, v.v.) và chuỗi kết nối động `SQLALCHEMY_DATABASE_URI`.
- Thêm `backend/app/core/database.py`: Khởi tạo SQLAlchemy Engine và Session.

### C. Cấu hình hệ thống Migration (Alembic)

- Sửa `backend/alembic/env.py`: Cấu hình để Alembic tự động đọc chuỗi kết nối từ `config.py` thay vì gán cứng (hard-code). Đồng thời nạp `target_metadata` từ các models đã tạo.
- Bổ sung `backend/alembic/script.py.mako`: File template bắt buộc để Alembic biết cách sinh ra file code migration.
- Thư viện: Thêm `psycopg2-binary` vào `requirements.txt` để Python có thể giao tiếp với PostgreSQL.
