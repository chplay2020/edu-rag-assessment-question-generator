# README_T028 — Process Material Endpoint (Backend)
## Contract endpoint

### `POST /api/v1/materials/{material_id}/process`

- Auth: Bearer token của Lecturer sở hữu course hoặc Admin.
- Material hợp lệ để bắt đầu: `uploaded` hoặc `failed`.
- Thành công: `202 Accepted`.
- Không tìm thấy hoặc Lecturer không sở hữu tài liệu: `404 Not Found`.
- Material đã `processing`, đã `processed`, hoặc đã có Job `process_material` ở `pending`/`running`: `409 Conflict`.

Response `202`:

```json
{
  "material_id": 9,
  "material_status": "processing",
  "job_id": 6,
  "job_status": "pending",
  "task_type": "process_material"
}
```

Có thể theo dõi Job bằng `GET /api/v1/jobs/{job_id}`. Endpoint Job áp dụng cùng quyền owner course/Admin.

## Luồng trạng thái

| Đối tượng | Trạng thái đầu | Sự kiện | Trạng thái cuối |
|---|---|---|---|
| Material | `uploaded`/`failed` | Endpoint chấp nhận request | `processing` |
| Job | chưa tồn tại | Endpoint tạo Job | `pending` |
| Job | `pending` | Worker claim Job | `running` |
| Material | `processing` | Pipeline thành công | `processed` |
| Job | `running` | Pipeline thành công | `done`, có `finished_at` |
| Material | `processing` | Pipeline lỗi | `failed` |
| Job | `running` | Pipeline lỗi | `failed`, có `finished_at` |

Worker ghi exception kèm `material_id` và `job_id` vào backend log. Bảng `jobs` hiện không có cột `error_message`

Các thay đổi DB của pipeline được flush rồi commit cùng trạng thái thành công. Nếu extract, clean, chunk, embedding hoặc Qdrant lỗi, transaction chứa các Chunk mới được rollback trước khi Material/Job được commit sang `failed`. File `raw.txt` hoặc `clean.txt` đã ghi trước lỗi có thể còn trên đĩa để chẩn đoán.

## Chống request và worker trùng

Endpoint thực hiện trong một transaction:

1. Đọc Material bằng `SELECT ... FOR UPDATE` trên PostgreSQL.
2. Trong lúc vẫn giữ row lock, kiểm tra quyền, trạng thái Material và Job `pending`/`running` hiện hữu.
3. Tạo Job `pending` và đổi Material sang `processing`.
4. Commit cả hai thay đổi cùng lúc.
5. Chỉ sau commit mới đăng ký `BackgroundTasks.add_task(...)`.

Hai request đồng thời cho cùng Material bị serialize trên row lock. Request thứ hai đọc lại trạng thái sau commit của request đầu và nhận `409`; không có cửa sổ “query trước rồi cùng insert”.

Worker cũng khóa Material và active Job khi claim. Worker chỉ chuyển Job `pending -> running`; nếu Job đã `running`, lần chạy worker trùng bị từ chối và không ghi đè Job/Material sang `failed`.

Unit test dùng SQLite nên `FOR UPDATE` không tạo row lock thực. Contract request trùng được test tuần tự trong unit test; hành vi đồng thời thực được kiểm tra riêng bằng E2E PostgreSQL bên dưới.

## Đường dẫn processed thống nhất

`app.core.storage.get_processed_dir()` là nguồn resolve duy nhất cho `raw.txt` và `clean.txt`:

- `PROCESSED_DIR` mặc định: `storage/processed`.
- Giá trị tương đối được resolve từ thư mục backend, không phụ thuộc current working directory.
- Docker: backend có `WORKDIR /app`, volume `./backend:/app`, nên đường dẫn trong container là `/app/storage/processed` và trên host là `backend/storage/processed`.
- Local chạy từ root repo hoặc từ `backend`: cùng ghi vào `<repo>/backend/storage/processed`.
- Cấu trúc mỗi tài liệu: `backend/storage/processed/material_<id>/raw.txt` và `clean.txt`.

`.env.example` và `docker-compose.yml` khai báo `PROCESSED_DIR=storage/processed`. `.gitignore` bỏ qua dữ liệu sinh trong đường dẫn chuẩn và cả đường dẫn legacy `storage/processed`, nhưng vẫn giữ `.gitkeep`.

Thư mục legacy `storage/processed/material_8/` đã tồn tại trước lần rà soát này. Không file nào trong đó bị xóa hay di chuyển.

## Kết quả test tự động

Chạy ngày 2026-08-14 trong backend container (Python 3.10.20):

```powershell
docker compose exec backend python -m pytest tests/test_material_process_api.py -v
# 16 passed, 7 warnings in 3.15s

docker compose exec backend python -m pytest -v
# 97 passed, 10 warnings in 4.73s
```

Warnings hiện có là deprecation warnings của Pydantic, SQLAlchemy và Starlette TestClient; không có test failure.

## Kết quả E2E thực tế

E2E chạy qua HTTP thật với PostgreSQL và Qdrant, không mock pipeline:

- Owner Lecturer: user `8`, `t028.e2e.ec5f2eb569@example.com`.
- Lecturer khác: user `9`, `t028.other.ec5f2eb569@example.com`.
- Course do owner tạo: `course_id=40`.
- File hợp lệ: TXT tiếng Việt `t028_e2e_real.txt`.
- File lỗi: `t028_e2e_broken.pdf` có nội dung PDF không hợp lệ.

### Pipeline thành công

- `material_id=9`, lần xử lý thành công dùng `job_id=6`.
- POST trả `202` với Material `processing`, Job `pending`, task type `process_material`.
- Polling quan sát được Job `pending -> running -> done`.
- Material cuối: `processed`.
- Job có `finished_at=2026-08-14T00:00:01.064133Z`.
- Material Detail trả `chunk_count=5` và `extracted_text_preview` có nội dung trích từ file thật.
- Có cả `backend/storage/processed/material_9/raw.txt` và `clean.txt`.
- Process lại sau khi hoàn tất trả `409`.

Lần E2E đầu tiên của Material 9 diễn ra khi service Qdrant chưa chạy và backend container cũ chưa nạp `QDRANT_URL`; các Job `1`, `2`, `4`, `5` đã chuyển `failed` đúng luồng. Sau khi Qdrant được khởi động và backend được recreate với cấu hình compose hiện tại, Job 6 hoàn tất. Các bản ghi và file test này được giữ lại, không tự xóa.

### Pipeline thất bại

- `material_id=10`, `job_id=3`.
- Job được quan sát `pending -> running -> failed`, có `finished_at=2026-08-13T23:56:01.057795Z`.
- Material cuối: `failed`.
- Backend log ghi lỗi PyMuPDF không thể mở PDF không hợp lệ, kèm Material/Job ID.

### Quyền và request đồng thời

- Lecturer user 9 process Material 9 của user 8 nhận `404`.
- Upload thêm Material `11`, gửi hai POST `/process` đồng thời: một request nhận `202` tạo Job `7`, request còn lại nhận `409`.
- Truy vấn PostgreSQL xác nhận Material 11 chỉ có đúng một Job `process_material`: `7:done`.

## Dữ liệu test đã phát sinh

Không tự động dọn các dữ liệu sau:

- Users `8`, `9`; course `40`; materials `9`, `10`, `11`; jobs `1` đến `7` liên quan E2E.
- Các upload `cd8a8915967f4ca8b9ab5559e8615999.txt`,
  `73c12760e2ac47eda8985a7b686f29cc.pdf` và
  `9c7468414dc344d79828c356415391aa.txt` trong `backend/storage/uploads/`.
- `backend/storage/processed/material_9/` và `material_11/`.
- Hai input test bị ignore trong `backend/storage/test-files/`.
- Thư mục legacy có sẵn từ trước: `storage/processed/material_8/`.

Nếu cần dọn, hãy xác nhận các ID/path trên thuộc dữ liệu test rồi xóa qua quy trình quản trị phù hợp; không nên xóa theo wildcard.

## Tự phục hồi tài liệu bị kẹt trạng thái `processing`

Nếu backend dừng đột ngột sau khi Material chuyển sang `processing` nhưng trước khi worker hoàn thành, Material có thể bị kẹt ở `processing` vô hạn dù không còn Job `pending`/`running` nào.

`app.services.material_service.recover_orphaned_processing_materials(db, material_ids)` tự động phát hiện và reset các Material này về `uploaded`:

- Được gọi tại `GET /api/v1/materials/course/{course_id}` và `GET /api/v1/materials/{id}`.
- Chỉ reset khi `status == "processing"` **và** không có Job `process_material` ở `pending`/`running`.
- Không reset nếu vẫn còn Job active (xử lý đang diễn ra bình thường).
- Sau khi reset, giảng viên thấy trạng thái "Đã tải lên" và có thể bấm "Xử lý tài liệu" lại.
- Commit ngay khi phát hiện orphan; các lần GET tiếp theo không thực hiện write thừa.

## Giới hạn MVP

`BackgroundTasks` chạy trong chính tiến trình backend. Nếu server dừng đột ngột sau khi transaction endpoint đã commit, Job có thể còn `pending` hoặc `running` và Material có thể còn `processing`. Cơ chế `recover_orphaned_processing_materials` xử lý trường hợp không còn Job active; giai đoạn sau có thể thay bằng queue worker như Celery/RQ cùng timeout, retry và job reconciliation.

Chi tiết lỗi chỉ có trong backend log vì schema Job hiện không có `error_message`. Ngoài ra DB và Qdrant không có distributed transaction; nếu Qdrant upsert thành công nhưng commit DB thất bại thì cần reconciliation ở kiến trúc worker bền vững hơn.
