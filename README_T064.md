# Báo cáo hoàn thành Task T064: Dashboard summary API

## 🎯 Mục tiêu
Cung cấp một Endpoint API tổng hợp số liệu để đổ dữ liệu ra giao diện Dashboard tổng quan. Đảm bảo phân quyền (RBAC) chặt chẽ giữa Admin (nhìn thấy tất cả) và Giảng viên (chỉ nhìn thấy số liệu khóa học của mình).

---

## 🛠️ Chi tiết triển khai

### 1. Schema DTO (Data Transfer Object)
- **File:** `backend/app/schemas/dashboard_schema.py`
- Tạo model `DashboardSummaryResponse` với các trường số học cơ bản:
  - `total_materials` (Tổng số tài liệu PDF/TXT)
  - `total_jobs` (Tổng số tiến trình sinh câu hỏi)
  - `total_generated_questions` (Tổng số câu hỏi được AI sinh ra)
  - `total_approved_questions` (Số câu hỏi được duyệt)
  - `total_rejected_questions` (Số câu hỏi bị từ chối)
  - `validation_avg_score` (Điểm trung bình chất lượng do AI Judge đánh giá)

### 2. Service Thống Kê & Phân Quyền
- **File:** `backend/app/services/dashboard_service.py`
- Sử dụng SQLAlchemy Query để `count()` dữ liệu.
- Cơ chế Phân quyền (RBAC):
  - Nhận diện Role của user thông qua Token.
  - Nếu role là `lecturer`, tự động `JOIN` các bảng `Material`, `Job`, `Question` sang bảng `Course`. Sau đó áp dụng bộ lọc `Course.created_by == user_id`. Như vậy, giảng viên chỉ nhìn thấy "vương quốc" của riêng mình.
- Xử lý điểm trung bình (Validation Avg Score):
  - Do hệ thống lưu điểm ở dạng JSON (từ LLM Judge của Task T046), việc tính trung bình SQL có thể thiếu linh hoạt.
  - Mình đã lấy list JSON ra và parse trực tiếp bằng logic Python để tính `validation_avg_score` chính xác nhất.

### 3. API Router
- **File:** `backend/app/api/routes/dashboard.py`
- **File:** `backend/app/api/main.py`
- Đăng ký API Route `GET /api/v1/dashboard/summary`. API được bảo vệ bởi dependency `Depends(get_current_user)`.

---

## 📌 Hướng dẫn Review / Test
1. Khởi động Backend: `docker compose up backend -d`
2. Sử dụng Frontend hoặc Postman, gọi API: `GET {{API_URL}}/api/v1/dashboard/summary` (nhớ đính kèm Bearer Token).
3. Payload JSON trả về sẽ có format:
```json
{
  "total_materials": 10,
  "total_jobs": 5,
  "total_generated_questions": 120,
  "total_approved_questions": 80,
  "total_rejected_questions": 5,
  "validation_avg_score": 8.5
}
```
4. Thử bằng 2 account khác nhau (Admin và một Lecturer bất kỳ) để thấy sự khác biệt về lượng dữ liệu trả về!
