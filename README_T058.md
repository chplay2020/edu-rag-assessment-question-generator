# README T058 – Trang Ngân hàng câu hỏi

## Phạm vi

Task T058 xây dựng trang **Ngân hàng câu hỏi** (`/question-bank`) – nơi giảng viên có thể tra cứu và chọn các câu hỏi **đã được duyệt** (status = `approved`) để chuẩn bị cho tính năng xuất đề thi (T061/T063).

| Trang | Route | Mục đích |
|---|---|---|
| Duyệt câu hỏi | `/questions` | Xem, chỉnh sửa, duyệt / từ chối câu hỏi |
| Ngân hàng câu hỏi | `/question-bank` | Chỉ xem câu đã duyệt, tìm kiếm, lọc, chọn để xuất |

---

## API sử dụng

**Endpoint:** `GET /api/v1/questions/bank`

**Query params được backend hỗ trợ:**

| Param | Kiểu | Mô tả |
|---|---|---|
| `course_id` | `int` | Lọc theo môn học |
| `difficulty` | `string` | `easy` / `medium` / `hard` |
| `bloom_level` | `string` | `remember` / `understand` / `apply` / `analyze` / `evaluate` / `create` |
| `question_type` | `string` | `multiple_choice` |
| `skip` | `int` | Phân trang – bỏ qua N bản ghi |
| `limit` | `int` | Phân trang – tối đa 200 bản ghi |

Tham khảo: [`backend/app/api/routes/question_bank.py`](backend/app/api/routes/question_bank.py)

---

## Các filter

- **Tìm kiếm nội dung**: Client-side, lọc theo chuỗi trong `content` của câu hỏi.
- **Môn học**: Dropdown lấy danh sách từ `GET /courses`, gửi `course_id` lên API.
- **Độ khó**: `easy` / `medium` / `hard`
- **Bloom**: 6 cấp độ tư duy Bloom
- **Loại câu hỏi**: Hiện chỉ có `multiple_choice`

`course_id` được đọc từ query string (`/question-bank?course_id=3`) để trang Môn học có thể điều hướng thẳng đến danh sách câu hỏi của môn đó.

---

## Chọn câu chuẩn bị cho export

- Checkbox từng câu và **Chọn tất cả** (các câu đang hiển thị sau filter/search).
- Badge đếm số câu đã chọn hiển thị trong thanh toolbar và trên nút Xuất Excel.
- Khi bỏ filter, tập hợp đã chọn được giữ nguyên (chỉ reset khi fetch API mới).

---

## Tính năng export

> **Export thật (Excel) thuộc T061 và T063 – không phải T058.**

Nút **Xuất Excel** hiển thị trên trang nhưng ở trạng thái `disabled`. Tooltip giải thích lý do:
> "Xuất Excel sẽ khả dụng sau khi hoàn thành T061 và T063."

Không có mock download hay giả lập nào được thực hiện.

---

## File đã thay đổi / tạo mới

| File | Thao tác | Mô tả |
|---|---|---|
| `frontend/src/services/questionBankApi.ts` | **Mới** | API client gọi `GET /questions/bank` |
| `frontend/src/pages/QuestionBank.tsx` | **Mới** | Trang Ngân hàng câu hỏi |
| `frontend/src/pages/QuestionBank.css` | **Mới** | Styles cho trang Question Bank |
| `frontend/src/App.tsx` | **Sửa** | Thêm route `/question-bank` |
| `frontend/src/layouts/MainLayout.tsx` | **Sửa** | Đổi tên sidebar `/questions` → "Duyệt câu hỏi", thêm mục "Ngân hàng câu hỏi" |
| `frontend/src/pages/CourseDetail.tsx` | **Sửa** | Kích hoạt nút "Xem câu hỏi" → `/question-bank?course_id=<id>` |

---

## Hướng dẫn test thủ công

1. **Sidebar**: Đăng nhập → kiểm tra sidebar có 2 mục riêng "Duyệt câu hỏi" (`/questions`) và "Ngân hàng câu hỏi" (`/question-bank`).

2. **Trang duyệt câu hỏi giữ nguyên**: Vào `/questions` → vẫn thấy đầy đủ nút Chỉnh sửa / Duyệt / Từ chối.

3. **Question Bank chỉ hiển thị câu approved**:
   - Vào `/question-bank`.
   - Kiểm tra không có nút Duyệt / Từ chối trên bất kỳ câu nào.
   - Kiểm tra tất cả câu hiển thị đều có trạng thái `approved` trong backend.

4. **Filter hoạt động**:
   - Chọn môn học → danh sách cập nhật theo môn.
   - Chọn độ khó "Dễ" → chỉ hiển thị câu `easy`.
   - Tìm kiếm từ khóa → chỉ hiển thị câu chứa từ khóa đó.

5. **Điều hướng từ môn học**:
   - Vào `/courses` → click vào một môn → click "Xem câu hỏi".
   - Xác nhận chuyển đến `/question-bank?course_id=<id>` và filter môn học đã được chọn sẵn.

6. **Chọn câu**:
   - Tick checkbox từng câu.
   - Tick "Chọn tất cả" → chọn hết câu đang hiển thị.
   - Bỏ chọn một câu → "Chọn tất cả" trở về trạng thái indeterminate-like (unchecked).
   - Badge đếm số câu đã chọn hiển thị đúng.

7. **Nút Xuất Excel bị khóa**:
   - Nút không thể click.
   - Hover → tooltip hiện "Xuất Excel sẽ khả dụng sau khi hoàn thành T061 và T063."

8. **Empty state**:
   - Chọn môn chưa có câu hỏi approved → hiển thị thông báo "Chưa có câu hỏi nào được duyệt".
   - Tìm kiếm chuỗi không tồn tại → hiển thị thông báo không tìm thấy.
