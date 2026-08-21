# Báo cáo hoàn thành Task T065: Dashboard cards/charts

## 🎯 Mục tiêu
Cung cấp một giao diện bảng điều khiển (Dashboard) trực quan trên Frontend. Dashboard sẽ không còn sử dụng dữ liệu tĩnh (mockup) mà trực tiếp "bơm" dữ liệu sống (live data) từ Backend, vẽ nên các Thẻ số liệu (Cards) và Đồ thị (Charts) sinh động.

---

## 🛠️ Chi tiết triển khai

### 1. Backend: Nâng cấp dữ liệu vẽ đồ thị
- **File:** `backend/app/schemas/dashboard_schema.py` & `backend/app/services/dashboard_service.py`
- Thay vì chỉ đếm tổng số, API Backend đã được nâng cấp thêm các thuật toán `GROUP BY` để bóc tách câu hỏi theo 3 khía cạnh:
  - Phân bổ theo mức độ khó (`questions_by_difficulty`)
  - Phân bổ theo thang nhận thức Bloom (`questions_by_bloom`)
  - Phân bổ theo trạng thái duyệt (`questions_by_status`)
- Các query vẫn bảo toàn nguyên tắc Phân quyền (RBAC) đã viết ở Task T064.

### 2. Frontend: Tích hợp thư viện & Tạo Service
- **NPM Package:** Install thành công thư viện **`recharts`** – công cụ vẽ biểu đồ chuyên nghiệp nhất nhì của hệ sinh thái React.
- **File:** `frontend/src/services/dashboardApi.ts`
- Định nghĩa interface `DashboardSummary` và hàm gọi axios `getDashboardSummary` để fetch dữ liệu từ API `/api/v1/dashboard/summary`.

### 3. Frontend: Vẽ Bức tranh Toàn cảnh
- **File:** `frontend/src/pages/Dashboard.tsx`
- Xóa hoàn toàn layout cứng cũ kỹ. Xây dựng Layout Grid xịn sò:
  - **Khu vực Top (Cards):** Bày binh bố trận 6 thẻ chỉ số: Tổng tài liệu, Tổng Job, Tổng câu hỏi, Đã duyệt, Bị từ chối và Điểm đánh giá AI trung bình. 
  - Gắn icon nổi bật từ `@phosphor-icons` và có màu sắc đặc trưng cho từng loại thẻ.
  - **Khu vực Middle (Charts):** Đặt 3 khung đồ thị lớn:
    - `PieChart` vòng tròn cho Trạng thái câu hỏi (đã map tên hiển thị Tiếng Việt: Đã duyệt, Từ chối, Nháp...).
    - `PieChart` tương tự cho Mức độ khó.
    - `BarChart` cột dọc để so sánh số lượng câu hỏi theo thang đo Bloom.
- Xử lý Loading State bài bản: hiển thị text "Đang tải dữ liệu..." trước khi biểu đồ bùng nổ trên màn hình nhờ các hiệu ứng Animation mượt mà.

---

## 📌 Hướng dẫn Review / Test
1. Khởi động Backend và Frontend.
2. Đăng nhập vào trình duyệt Frontend `http://localhost:5173`.
3. Bạn sẽ được điều hướng vào ngay trang Tổng Quan (`/`).
4. Quan sát các con số tổng và hover chuột vào các biểu đồ tròn/biểu đồ cột để thấy tooltip chi tiết hiện lên. 
5. Cứ thử sinh thêm 1 vài câu hỏi mới ở các Material khác nhau, sau đó ra F5 lại Dashboard để thấy các biểu đồ nhảy múa!
