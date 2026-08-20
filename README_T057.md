# README T057 – Question Bank API

## Mục tiêu
Cung cấp endpoint truy vấn **Question Bank** — danh sách câu hỏi đã được duyệt (`status = "approved"`) — cho giảng viên và admin tra cứu, lọc và phân trang.

## Endpoint
GET /api/v1/questions/bank
### Query Parameters

| Tham số         | Kiểu    | Bắt buộc | Mô tả                                        |
|-----------------|---------|----------|----------------------------------------------|
| `course_id`     | integer | Không    | Lọc theo môn học                              |
| `difficulty`    | string  | Không    | `easy` \| `medium` \| `hard`                 |
| `bloom_level`   | string  | Không    | Bloom taxonomy level (remember, analyze, ...) |
| `question_type` | string  | Không    | `multiple_choice` \| ...                     |
| `skip`          | integer | Không    | Số bản ghi bỏ qua (mặc định: 0, min: 0)      |
| `limit`         | integer | Không    | Số bản ghi trả về (mặc định: 20, max: 200)   |

Tất cả filter đều optional và có thể kết hợp tùy ý.

---

## Quy tắc chỉ trả `approved`

- Filter cứng: `WHERE questions.status = 'approved'`
- Câu hỏi ở trạng thái `draft`, `review_required`, hoặc `rejected` **không bao giờ** xuất hiện trong kết quả.
- Logic này nằm trong service [`question_bank_service.py`](backend/app/services/question_bank_service.py), constant `APPROVED_STATUS = "approved"`.

---

## Cấu trúc Response

```json
[
  {
    "id": 1,
    "content": "Nội dung câu hỏi?",
    "difficulty": "medium",
    "bloom_level": "remember",
    "question_type": "multiple_choice",
    "explanation": "...",
    "source_chunk_ids": [1, 2],
    "status": "approved",
    "material_id": 3,
    "course_id": 2,
    "job_id": 5,
    "created_at": "2026-08-19T10:00:00Z",
    "options": [
      { "id": 1, "question_id": 1, "content": "Đáp án A", "is_correct": true },
      { "id": 2, "question_id": 1, "content": "Đáp án B", "is_correct": false }
    ]
  }
]
```

Tái sử dụng `QuestionResponse` schema hiện có (bao gồm `options`).

Sắp xếp: `created_at DESC, id DESC` (mới nhất trước, ổn định kể cả khi timestamp trùng).

---

## Phân quyền

Endpoint yêu cầu người dùng đã xác thực với role `lecturer` hoặc `admin` (dependency `get_current_active_lecturer`).

Không có xác thực → HTTP 401.

---

## Files đã tạo / sửa

| File | Thay đổi |
|------|----------|
| [`backend/app/services/question_bank_service.py`](backend/app/services/question_bank_service.py) | **[NEW]** Service: query `approved`, filter, phân trang, sort |
| [`backend/app/api/routes/question_bank.py`](backend/app/api/routes/question_bank.py) | **[NEW]** Route: `GET /bank` với Query params |
| [`backend/app/api/main.py`](backend/app/api/main.py) | **[MODIFY]** Đăng ký `question_bank` router trước `questions` router để `/bank` không bị path param `/{question_id}` chiếm |
| [`backend/tests/test_question_bank_api.py`](backend/tests/test_question_bank_api.py) | **[NEW]** 11 test cases |

---

## Tránh xung đột route

`/questions/bank` được include vào `api_router` **trước** `/questions` router có `/{question_id}`. FastAPI khớp route theo thứ tự khai báo, nên `/bank` sẽ không bị interpret là `question_id = "bank"`.

---

## Các test đã chạy và kết quả

```
tests/test_question_bank_api.py  11 passed
Full backend: 115 passed, 0 failed
```

| # | Test | Kết quả |
|---|------|---------|
| 1 | Không filter → chỉ trả `approved` | ✅ PASS |
| 2 | `draft` và `rejected` không xuất hiện | ✅ PASS |
| 3 | Filter theo `course_id` | ✅ PASS |
| 4 | Filter theo `difficulty` | ✅ PASS |
| 5 | Filter theo `bloom_level` | ✅ PASS |
| 6 | Filter theo `question_type` | ✅ PASS |
| 7 | Kết hợp nhiều filter | ✅ PASS |
| 8 | Không có kết quả → danh sách rỗng `[]` | ✅ PASS |
| 9 | Phân trang `skip`/`limit` | ✅ PASS |
| 10 | Auth: không có token → 401 | ✅ PASS |
| 11 | Sắp xếp mới nhất trước | ✅ PASS |

---

## Cảnh báo / Phần chưa kiểm tra

- Warnings (không phải lỗi):
  - Pydantic `class-based Config` deprecated → từ code hiện có trước T057, không sửa.
  - SQLAlchemy `declarative_base()` deprecated → từ code hiện có, không sửa.
  - Qdrant client version incompatible → từ test `test_question_generation_worker.py`, không liên quan T057.
- Chưa có **integration test** với PostgreSQL thật (chỉ SQLite in-memory).
- Chưa có test với Docker (`docker compose exec backend python -m pytest`) vì môi trường Docker chưa khả dụng trong session này.
- Không làm frontend, export, hay review workflow.
