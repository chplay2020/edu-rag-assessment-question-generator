# Báo cáo thay đổi: UI Frontend – Nâng cấp giao diện cao cấp

> **Ngày cập nhật:** 15/07/2026  
> **Phạm vi:** Toàn bộ giao diện frontend (`/frontend/src`)

---

## ⚠️ Lưu ý quan trọng – Dữ liệu Mockup

> Tất cả dữ liệu hiển thị trên giao diện hiện tại **đều là dữ liệu giả (mockup data)**, chỉ phục vụ mục đích xem trước thiết kế (UI preview). Dữ liệu này **không kết nối với backend hay database thật**.

| Màn hình | Dữ liệu giả hiện tại |
|---|---|
| Dashboard – Thẻ thống kê | Tổng số môn học: **12**, Tài liệu đã tải lên: **48**, Câu hỏi đã tạo: **1,204** |
| Dashboard – Tăng trưởng | +2 môn mới học kỳ này, +6 tài liệu tuần này, +128 câu sinh trong 24h |
| Trang đăng nhập | Email: `admin@edurag.com`, Mật khẩu: `password` |
| Header | "Chào mừng trở lại, Giảng viên" (tên người dùng cứng) |

Dữ liệu thật sẽ được tích hợp sau khi kết nối API backend hoàn chỉnh.

---

## Tổng quan thay đổi

Đợt cập nhật này tập trung vào nâng cấp toàn diện giao diện theo hướng **tối giản, cao cấp (premium minimalist)**, lấy cảm hứng từ phong cách thiết kế của Linear và Apple. Không có thay đổi nào về logic nghiệp vụ hay kết nối backend.

---

## Thay đổi chi tiết

### 1. Phông chữ – `frontend/src/index.css`

- **Đổi phông chữ toàn bộ ứng dụng** sang **Be Vietnam Pro** (Google Fonts).
- Be Vietnam Pro được thiết kế dành riêng cho tiếng Việt, đồng thời đẹp với cả tiếng Anh – phù hợp với sản phẩm song ngữ.
- Load weights: 300, 400, 500, 600, 700, 800.

---

### 2. Trang đăng nhập – `frontend/src/pages/Login.tsx` & `Login.css`

#### Bố cục & Khoảng trắng
- Tăng padding card từ `48px 40px` → `56px 48px` để tạo cảm giác "thở" cao cấp hơn.
- Giảm chiều rộng tối đa card từ `440px` → `420px` để tỷ lệ cân đối hơn.
- Tăng khoảng cách giữa các form group từ `20px` → `24px`.

#### Bảng màu
- Chuyển từ bảng màu xanh tím công nghiệp (`#1e40af`) sang bảng màu **Zinc** (trắng ngà + đen sắc nét):
  - Nền trang: `#fcfcfc` (trắng ngà nhẹ thay vì xám xanh)
  - Card: `#ffffff` với viền `rgba(0,0,0,0.06)` và shadow siêu mịn
  - Màu chữ chính: `#09090b` (Zinc 950)
  - Màu chữ phụ: `#71717a` (Zinc 500)
- Loại bỏ nền kính mờ (`glassmorphism`) vì không phù hợp phong cách tối giản.

#### Input
- Nền input: `#fafafa` (Zinc 50), viền nhạt `#e4e4e7`
- Khi focus: viền và icon bên trong chuyển đen `#09090b` + glow 1px
- Padding tăng từ `12px` → `14px` để vùng nhấn thoải mái hơn
- Border-radius input tăng từ `10px` → `12px` nhất quán với card

#### Nút Đăng nhập (CTA)
- Đổi màu nền nút sang đen `#09090b` (thay vì xanh dương `#1e40af`)
- **Bỏ icon** `SignIn` ra khỏi nút để trông tối giản hơn
- Thêm hiệu ứng nhấn: `scale(0.98)` + `translateY(1px)` khi click
- Border-radius nút: `12px` nhất quán với input

#### Icon con mắt (hiện/ẩn mật khẩu)
- **Sửa logic icon**: Khi mật khẩu đang ẩn → hiện icon `Eye` (mở). Khi mật khẩu hiển thị → hiện icon `EyeSlash` (gạch chéo).
- Dọn dẹp inline style sang class `.password-toggle-btn` trong CSS.

#### Thêm tính năng
- Thêm dòng **"Ghi nhớ đăng nhập"** (checkbox) và **"Quên mật khẩu?"** (link) giữa form và nút đăng nhập.

#### Logo trang đăng nhập
- Loại bỏ `margin` âm (hack CSS) trên logo → resize về `36x36px` tỷ lệ chuẩn.

---

### 3. Sidebar – `frontend/src/layouts/MainLayout.css`

#### Logo & Tên ứng dụng
- **Sửa lỗi lệch vị trí**: Loại bỏ `margin` âm trên `.sidebar-logo`, resize về `36x36px` với kích thước thực.
- Điều chỉnh `padding-top` sidebar từ `32px` → `18px` để logo và tên web ngang hàng chính xác với dòng chữ "Chào mừng trở lại" trên header.

---

### 4. Dashboard – `frontend/src/pages/Dashboard.tsx`

#### Thẻ thống kê (Stat Cards)
- **Giảm độ dày chữ số** từ `fontWeight: 800` (ExtraBold) → `fontWeight: 600` (SemiBold) cho các số liệu lớn (12, 48, 1,204).
- Tinh chỉnh `letter-spacing` từ `-0.03em` → `-0.04em` để các số liệu hiển thị gọn gàng và cân đối hơn.

---

## File thay đổi

| File | Loại thay đổi |
|---|---|
| `frontend/src/index.css` | Đổi phông chữ sang Be Vietnam Pro |
| `frontend/src/pages/Login.tsx` | Cấu trúc JSX, thêm checkbox/link, sửa icon mắt |
| `frontend/src/pages/Login.css` | Toàn bộ bảng màu và spacing premium |
| `frontend/src/layouts/MainLayout.css` | Sửa logo alignment, sidebar padding |
| `frontend/src/pages/Dashboard.tsx` | Font weight thẻ thống kê |

---

## Hướng tiếp theo

- [ ] Kết nối API thật để thay thế mockup data trên Dashboard
- [ ] Tích hợp xác thực JWT cho trang đăng nhập (hiện tại chỉ lưu `localStorage`)
- [ ] Áp dụng design system nhất quán cho các trang còn lại (`/questions`, `/courses`)
