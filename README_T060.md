# Task T060: Review testing

## 1. Tổng quan
Task T060 thuộc nhóm DevOps/QA với mục tiêu là kiểm thử luồng đánh giá câu hỏi (Review Workflow) do hệ thống AI sinh ra. Luồng này bao gồm các chức năng quan trọng dành cho Giảng viên: Chỉnh sửa nội dung câu hỏi, Phê duyệt (Approve), Từ chối (Reject), Lọc (Filter) theo trạng thái, và kiểm soát phân quyền truy cập (Permission).

Nhằm đảm bảo tính chính xác và an toàn tuyệt đối cho ngân hàng câu hỏi, thay vì chỉ kiểm thử thủ công trên giao diện (UI), dự án đã quyết định phát triển một bộ kiểm thử tích hợp tự động (Automated Integration Test Suite) bằng framework `pytest` ở tầng Backend.

## 2. Các kịch bản kiểm thử (Test Cases) đã triển khai

Bộ kiểm thử bao gồm 5 kịch bản tự động chính, được lập trình trong file `backend/tests/test_review_workflow.py`:

| ID | Test Case | Mục đích & Kết quả mong đợi | Trạng thái |
|---|---|---|---|
| TC1 | Phân quyền truy cập | Ngăn chặn hành vi "xem lén", duyệt hoặc sửa câu hỏi của một Giảng viên trên khóa học mà họ không quản lý. (Kỳ vọng: Lỗi 403 Forbidden hoặc 404 Not Found). | `PASS` |
| TC2 | Bộ lọc trạng thái | Kiểm tra API danh sách câu hỏi lọc chính xác theo các trạng thái: `draft`, `review_required`, `approved`, `rejected`. | `PASS` |
| TC3 | Phê duyệt và Từ chối | Kiểm thử việc gọi API `POST /questions/{id}/review` với hành động Approve. Câu hỏi phải chuyển trạng thái sang `approved` và sinh ra một dòng nhật ký (Review Log) thành công trong Database. | `PASS` |
| TC4 | Cập nhật nội dung | Kiểm thử chức năng sửa đề dẫn (Stem) và sửa các đáp án (Options). Đảm bảo logic tính toán đáp án đúng (`is_correct`) được lưu lại chuẩn xác trong CSDL. | `PASS` |
| TC5 | Tự động hạ cấp | **(Tính năng tự bảo vệ)** Khi một câu hỏi đang ở trạng thái Đã duyệt (`approved`) bị thay đổi nội dung, hệ thống phải ngay lập tức hạ cấp nó xuống `draft` hoặc `review_required` để bắt buộc quy trình duyệt lại từ đầu, ngăn chặn việc sửa lén đề thi. | `PASS` |

## 3. Quá trình thực thi và Kết quả

**Thời gian thực thi:** Week 6 (Tháng 8/2026)
**Công cụ sử dụng:** FastAPI TestClient, Pytest, SQLAlchemy StaticPool (In-memory SQLite).

**Kết quả chạy Test Suite:**
```bash
$ python -m pytest backend/tests/test_review_workflow.py -v

============================= test session starts =============================
platform win32 -- Python 3.11.6, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\edu-rag-assessment-question-generator
plugins: anyio-4.14.2
collecting ... collected 5 items

backend/tests/test_review_workflow.py::test_other_lecturer_cannot_access_question PASSED [ 20%]
backend/tests/test_review_workflow.py::test_filter_questions_by_status PASSED [ 40%]
backend/tests/test_review_workflow.py::test_review_question PASSED       [ 60%]
backend/tests/test_review_workflow.py::test_edit_question_updates_options PASSED [ 80%]
backend/tests/test_review_workflow.py::test_edit_approved_question_downgrades_to_draft PASSED [100%]

======================= 5 passed, 10 warnings in 10.77s =======================
```

## 4. Kết luận
Luồng Đánh giá Câu hỏi (Review Workflow) đã hoạt động cực kỳ ổn định và chặt chẽ, vượt qua 100% các tiêu chuẩn kiểm thử khắt khe (Test checklist pass). Không phát hiện lỗ hổng phân quyền hay lỗi logic trạng thái. 

Task T060 chính thức **Hoàn thành (Done)**.
