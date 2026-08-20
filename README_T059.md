# README T059 – Prevent Rejected Questions in Bank (Backend)

## Mục tiêu

T059 bổ sung lớp bảo vệ dữ liệu cho Question Bank API:

- **Chỉ câu hỏi có `status = "approved"`** mới được xuất hiện trong Ngân hàng câu hỏi.
- **`draft`, `review_required`, `rejected`** bị chặn hoàn toàn – không có cách nào lấy chúng qua endpoint này.
- **Lecturer chỉ thấy câu hỏi thuộc course do chính họ tạo** (`course.created_by == current_user.id`).
- **Admin** thấy toàn bộ câu hỏi `approved` của mọi course.

## Quy tắc status

| Status | Được vào Question Bank? |
|---|---|
| `draft` | ❌ Không |
| `review_required` | ❌ Không |
| `approved` | ✅ Có |
| `rejected` | ❌ Không |

## Liên hệ giữa các Task

| Task | Vai trò |
|---|---|
| **T057** | Xây dựng `GET /api/v1/questions/bank` – API cơ bản trả câu approved, filter, phân trang |
| **T058** | Trang frontend `/question-bank` – hiển thị kết quả từ T057 |
| **T059** | Thêm lớp bảo vệ backend: phân quyền owner, helper `get_exportable_questions()` |
| **T061** | Tạo tính năng export Excel (sẽ dùng `get_exportable_questions()` từ T059) |
| **T063** | Giao diện frontend cho export (T061/T063 chưa làm) |

## Thay đổi trong T059

### `backend/app/services/question_bank_service.py`

- Thêm `_base_approved_query()`: query cơ sở luôn lọc `status='approved'` và `course.is_deleted=False`.
- Thêm `_apply_ownership_filter()`: lọc theo `created_by` nếu role là `lecturer`; admin không bị lọc.
- Cập nhật `get_question_bank()`: nhận thêm tham số `current_user`, áp dụng 2 helper trên.
- Thêm `get_exportable_questions()`: helper cho T061/T063, nhận danh sách `question_ids`, trả câu approved thuộc course của user. Nếu có ID nào không hợp lệ (draft, rejected, của người khác, hoặc không tồn tại), raise `HTTP 422` với danh sách `invalid_question_ids`.

### `backend/app/api/routes/question_bank.py`

- Thêm `current_user: User = Depends(get_current_active_lecturer)` vào signature.
- Truyền `current_user` vào `question_bank_service.get_question_bank()`.

### `backend/tests/test_question_bank_api.py`

- Refactor helper functions để tái sử dụng (`_make_user`, `_make_course`, `_make_material`).
- Giữ nguyên 10 test T057 (đều pass).
- Thêm 9 test mới cho T059:
  - Ownership isolation (lecturer A không thấy course của lecturer B).
  - Admin thấy tất cả nhưng chỉ approved.
  - Filter không làm lộ câu hỏi của lecturer khác.
  - `get_exportable_questions()` trả đúng câu approved.
  - `get_exportable_questions()` raise 422 khi có câu draft/rejected.
  - `get_exportable_questions()` raise 422 khi có câu của lecturer khác.
  - `get_exportable_questions()` với list rỗng trả list rỗng.
  - `get_exportable_questions()` raise 422 khi ID không tồn tại.

## Kết quả Test

```
collected 20 items

tests/test_question_bank_api.py::test_bank_returns_only_approved          PASSED
tests/test_question_bank_api.py::test_bank_excludes_draft_and_rejected    PASSED
tests/test_question_bank_api.py::test_bank_filter_by_course_id            PASSED
tests/test_question_bank_api.py::test_bank_filter_by_difficulty           PASSED
tests/test_question_bank_api.py::test_bank_filter_by_bloom_level          PASSED
tests/test_question_bank_api.py::test_bank_filter_by_question_type        PASSED
tests/test_question_bank_api.py::test_bank_combined_filters               PASSED
tests/test_question_bank_api.py::test_bank_empty_when_no_approved         PASSED
tests/test_question_bank_api.py::test_bank_pagination                     PASSED
tests/test_question_bank_api.py::test_bank_requires_auth                  PASSED
tests/test_question_bank_api.py::test_bank_ordered_newest_first           PASSED
tests/test_question_bank_api.py::test_bank_lecturer_cannot_see_other_course   PASSED
tests/test_question_bank_api.py::test_bank_admin_sees_all_courses         PASSED
tests/test_question_bank_api.py::test_bank_filters_dont_expose_other_lecturer_questions  PASSED
tests/test_question_bank_api.py::test_exportable_returns_approved_ids     PASSED
tests/test_question_bank_api.py::test_exportable_rejects_draft_ids        PASSED
tests/test_question_bank_api.py::test_exportable_rejects_rejected_ids     PASSED
tests/test_question_bank_api.py::test_exportable_rejects_other_lecturer_ids   PASSED
tests/test_question_bank_api.py::test_exportable_empty_list               PASSED
tests/test_question_bank_api.py::test_exportable_nonexistent_id_raises    PASSED

20 passed, 12 warnings in 3.05s
```

> Warnings là Pydantic v2 deprecation và Starlette constant rename – pre-existing, không phải do T059.

## Cảnh báo còn lại

- `HTTP_422_UNPROCESSABLE_ENTITY` sẽ được rename thành `HTTP_422_UNPROCESSABLE_CONTENT` trong Starlette mới hơn – chỉ là tên constant, giá trị `422` không đổi. Có thể sửa khi upgrade Starlette.
- Không tạo migration vì không có schema change.
