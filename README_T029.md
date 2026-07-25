# README – T029: Material Processing Status UI (MOCK)

> Giao diện này chỉ giả lập luồng xử lý tài liệu để kiểm tra UI/UX.
> API T028 (`POST /api/v1/materials/{material_id}/process`) **chưa** được tích hợp.

---

## 1. Trạng thái đã mô phỏng

| Trạng thái | Nhãn hiển thị | Màu dot | Mô tả |
|---|---|---|---|
| `pending` | Chờ xử lý | 🟡 vàng | Ngay sau khi bấm Xác nhận (~400 ms) |
| `processing` | Đang xử lý | 🟡 vàng | Spinner quay, nút bị disable (~3–5 giây) |
| `done` | Đã xử lý | 🟢 xanh | Badge xanh, preview text giả, chunk_count > 0 |
| `failed` | Xử lý thất bại | 🔴 đỏ | Banner lý do lỗi, nút "Thử lại" |

---

## 2. Cách bật kịch bản thành công / thất bại

### Kịch bản thành công (mặc định)
1. Mở trang chi tiết tài liệu.
2. Bấm **"Xử lý tài liệu"**.
3. **Không** tích checkbox "Giả lập kịch bản thất bại".
4. Bấm **"Xác nhận xử lý"**.
5. Quan sát: `pending` → `processing` (3–5 giây) → `done`.
6. Kiểm tra: badge xanh "Đã xử lý", `chunk_count` tăng, preview text xuất hiện.

### Kịch bản thất bại
1. Bấm **"Xử lý tài liệu"**.
2. **Tích** checkbox **"[Mock] Giả lập kịch bản thất bại"**.
3. Bấm **"Xác nhận xử lý"**.
4. Quan sát: `pending` → `processing` (3–5 giây) → `failed`.
5. Kiểm tra: badge đỏ "Xử lý thất bại", banner lý do lỗi, nút "Thử lại" xuất hiện.

### Kịch bản thử lại sau thất bại
1. Sau khi gặp `failed`, bấm **"Thử lại"**.
2. Modal xác nhận xuất hiện lại.
3. Có thể bật/tắt kịch bản thất bại để kiểm thử vòng lặp.

---

## 3. Kiểm tra chuyển trang trong lúc xử lý

1. Bấm Xác nhận Xử lý → mock bắt đầu chạy.
2. Chuyển sang trang khác (ví dụ: danh sách tài liệu).
3. Quay lại trang chi tiết.
4. UI sẽ đọc lại trạng thái từ `sessionStorage` / memory store.
5. Nếu xử lý đã xong: hiển thị trạng thái cuối (done/failed).
6. Nếu đang xử lý: polling 600 ms sẽ tiếp tục cho đến khi xong.

---

## 4. Tổ chức mock service

```
frontend/src/mocks/
└── materialProcessingMock.ts    ← toàn bộ logic mock tập trung tại đây
```

### Các hàm export

| Hàm | Mô tả |
|---|---|
| `getMockState(materialId)` | Đọc trạng thái hiện tại (memory → sessionStorage) |
| `resetMockState(materialId)` | Xóa trạng thái một tài liệu |
| `resetAllMockStates()` | Xóa toàn bộ trạng thái mock |
| `mockProcessMaterial(id, opts, onTransition?)` | Giả lập luồng xử lý, trả Promise |

### Lưu trữ
- **Memory**: `Map<number, MockProcessingState>` – nhanh, không persist qua F5.
- **sessionStorage**: backup tự động – persist khi navigate nhưng mất khi đóng tab.

---

## 5. Những phần cần thay khi API T028 hoàn thành

### 5.1. Gọi API thật thay mockProcessMaterial

```typescript
// TRƯỚC (mock)
await mockProcessMaterial(materialId, options, onTransition);

// SAU (API thật)
await apiClient.post(`/materials/${materialId}/process`);
```

### 5.2. Poll trạng thái thật thay polling mock

```typescript
// TRƯỚC (mock polling – check sessionStorage/memory)
const state = getMockState(mId);

// SAU (API polling)
const data = await getMaterialById(mId);
// Dừng khi data.status 'done' | 'failed'
```

### 5.3. Đọc chunk_count và extracted_text_preview từ API thật

```typescript
// TRƯỚC (mock)
setMockChunkCount(state.chunkCount);
setMockPreviewText(state.extractedTextPreview);

// SAU (API)
setMaterial(materialData);  // dữ liệu thật từ GET /materials/{id}
```

### 5.4. Xóa mock service và imports

Sau khi tích hợp xong:
- Xóa `frontend/src/mocks/materialProcessingMock.ts`
- Xóa các import từ mock trong `MaterialDetail.tsx`
- Xóa các state mock: `mockStatus`, `mockFailureReason`, `mockChunkCount`, `mockPreviewText`
- Xóa modal checkbox "Giả lập kịch bản thất bại"
- Dùng trực tiếp `material.status`, `material.chunk_count`, `material.extracted_text_preview`

### Endpoints cần tích hợp (T028)

```
POST /api/v1/materials/{material_id}/process
GET  /api/v1/materials/{material_id}          ← poll đến khi status = done | failed
```

---

## 6. Danh sách file đã tạo / sửa

| File | Thao tác | Mô tả |
|---|---|---|
| `frontend/src/mocks/materialProcessingMock.ts` | **TẠO MỚI** | Mock service: lưu trạng thái, giả lập timing |
| `frontend/src/pages/MaterialDetail.tsx` | **SỬA** | Kích hoạt nút, thêm modal, toast, polling, timer cleanup |
| `frontend/src/pages/MaterialDetail.css` | **SỬA** | Toast, modal, btn-retry, btn-done, failure banner, md-spin |
| `frontend/src/pages/CourseMaterials.tsx` | **SỬA** | StatusBadge: thêm done/failed/completed mapping |
| `frontend/src/pages/CourseMaterials.css` | **SỬA** | Thêm `.cm-status-done` và `.cm-status-failed` |
| `README_T029.md` | **TẠO MỚI** | Tài liệu này |

---

## 7. Kết quả lint / build

```
npm run lint  → 0 errors, 1 warning (cũ, không liên quan T029)
tsc -b --noEmit → 0 errors, 0 warnings
npm run build → ✓ built in ~864ms
```

---

## 8. Danh sách kiểm tra thủ công

- [x] Ban đầu chưa xử lý → nút "Xử lý tài liệu" enabled
- [x] Bấm nút → modal xác nhận xuất hiện, có toggle thất bại
- [x] Xác nhận → `pending` → `processing` (spinner, nút disable)
- [x] Sau 3–5s → `done`: badge xanh, chunk_count > 0, preview text hiện
- [x] Kịch bản thất bại → `failed`: badge đỏ, lý do, nút "Thử lại"
- [x] Thử lại → mở lại modal, có thể chọn lại kịch bản
- [x] Chuyển trang rồi quay lại → trạng thái được khôi phục
- [x] Nút tải xuống hoạt động bình thường (không bị ảnh hưởng)
- [x] Không có lỗi console
- [x] Không còn timer sau unmount (isMountedRef guard)
- [x] Responsive desktop & mobile (kế thừa CSS hiện có)
- [x] aria-label, role="dialog", aria-live trên toast

---

## 9. Kết luận

> **Mock UI T029 đã hoàn thành.**
> **T029 thật vẫn chờ API T028.**
>
> Khi T028 hoàn thành (POST /api/v1/materials/{id}/process), cần:
> 1. Thay thế `mockProcessMaterial` bằng lời gọi API thật.
> 2. Thay polling mock bằng poll GET /materials/{id} (hoặc WebSocket nếu có).
> 3. Xóa file mock và dọn state mock khỏi component.
> 4. Đánh dấu T029 Done sau khi test end-to-end thành công.
