# README T029 — Frontend Process Material + Polling trạng thái Job

## Mục tiêu

Cho phép người dùng xử lý tài liệu từ trang chi tiết, theo dõi tiến trình qua polling job và tự động cập nhật nội dung sau khi worker hoàn thành. Không dùng mock data.

---

## API được sử dụng

| Mục đích | Method | Endpoint |
|---|---|---|
| Yêu cầu xử lý tài liệu | `POST` | `/api/v1/materials/{material_id}/process` |
| Lấy trạng thái job | `GET` | `/api/v1/jobs/{job_id}` |
| Lấy chi tiết material | `GET` | `/api/v1/materials/{material_id}` |

### Response `POST /process` (202 Accepted)
```json
{
  "material_id": 12,
  "material_status": "processing",
  "job_id": 8,
  "job_status": "pending",
  "task_type": "process_material"
}
```

### Response `GET /jobs/{job_id}` (200 OK)
```json
{
  "id": 8,
  "material_id": 12,
  "task_type": "process_material",
  "status": "done",
  "created_at": "2026-08-15T02:00:00",
  "finished_at": "2026-08-15T02:01:00"
}
```

---

## Luồng hoạt động

```
Người dùng nhấn "Xử lý tài liệu"
    ↓
POST /materials/{id}/process
    ↓ 202 Accepted
Nhận job_id  →  processPhase = 'polling'
    ↓
setTimeout 2s → GET /jobs/{job_id}
    ↓
job.status == 'pending' | 'running' → lặp lại setTimeout 2s
job.status == 'done'   → GET /materials/{id} → cập nhật UI → thông báo thành công
job.status == 'failed' → hiển thị lỗi → nút "Thử lại"
```

---

## Mapping trạng thái

### Material
| Giá trị backend | Hiển thị tiếng Việt |
|---|---|
| `uploaded` | Chưa xử lý |
| `processing` | Đang xử lý |
| `processed` | Đã xử lý |
| `failed` | Xử lý thất bại |

### Job
| Giá trị backend | Hiển thị tiếng Việt |
|---|---|
| `pending` | Đang chờ |
| `running` | Đang xử lý |
| `done` | Hoàn thành |
| `failed` | Thất bại |

---

## Xử lý lỗi

| Tình huống | Hành vi |
|---|---|
| `404` khi process | Hiển thị "Không tìm thấy tài liệu hoặc bạn không có quyền truy cập." |
| `409` khi process | Thông báo "Tài liệu đang được xử lý", không tạo job mới |
| Lỗi mạng khi polling | Tự động thử lại sau 2 giây (không dừng polling) |
| Job failed | Hiển thị thông báo lỗi, nút đổi thành "Thử lại" |
| Lỗi server (5xx) | Dừng xử lý, hiển thị thông báo, cho phép thử lại |

---

## Cơ chế dừng polling

- Dùng `setTimeout` (không phải `setInterval`) để đảm bảo chỉ có **một timer** tại một thời điểm.
- `pollingTimerRef` giữ reference của timer hiện tại.
- `stopPolling()` hủy timer ngay khi:
  - Component unmount
  - `materialId` thay đổi (chuyển trang)
  - Job kết thúc (`done` hoặc `failed`)
- `isMountedRef` ngăn setState sau khi component đã unmount.

---

## Files đã thay đổi

| File | Thay đổi |
|---|---|
| `frontend/src/utils/materialStatus.ts` | Sửa `uploaded → Chưa xử lý`; thêm `getJobStatusMeta`, `getJobStatusLabel` |
| `frontend/src/services/materialApi.ts` | Thêm `MaterialProcessResponse`, `JobResponse`, `processMaterial()`, `getJobById()`; cập nhật cache list trong `getMaterialById` |
| `frontend/src/pages/MaterialDetail.tsx` | Xóa toàn bộ mock, thêm real API + polling |
| `frontend/src/pages/CourseMaterials.tsx` | Fix useEffect dependency để luôn fetch mới khi navigate về |
| `README_T029.md` | Tài liệu này |

---

## Kết quả kiểm thử (thủ công)

Chạy `npm run lint` và `npm run build` để xác nhận không có lỗi TypeScript/ESLint.

Các test case cần kiểm tra thủ công khi backend chạy:

1. Material `uploaded` → nhấn "Xử lý tài liệu" → nhận `202`, UI chuyển sang "Đang xử lý".
2. Polling mỗi 2 giây → khi job `done` → UI hiển thị "Đã xử lý", chunk_count và preview từ API thật.
3. Nhấn xử lý trùng (material đang `processing`) → API trả `409` → UI báo lỗi, không tạo job mới.
4. Job `failed` → UI hiển thị lỗi + nút "Thử lại".
5. Reload trang trong lúc `processing` → hiển thị đúng trạng thái (xem giới hạn bên dưới).
6. Navigate về danh sách → trạng thái mới nhất được hiển thị (fetch lại từ API).
7. Chuyển sang tài liệu khác → polling timer dừng, không leak.
8. Không còn chữ trạng thái tiếng Anh hay dữ liệu mock trên UI.

---

## Giới hạn còn lại

> **Polling không tự phục hồi sau reload trang khi material đang `processing`.**
>
> Backend endpoint `GET /api/v1/materials/{id}` không trả `job_id` hiện tại trong response.
> Do đó, nếu người dùng reload trang khi material đang ở trạng thái `processing`,
> frontend chỉ hiển thị đúng trạng thái `processing` (từ `material.status`)
> nhưng **không thể tự động tiếp tục polling** vì không biết `job_id`.
>
> **Giải pháp khi backend hỗ trợ**: Thêm trường `active_job_id` vào `MaterialDetailResponse`
> để frontend lấy job_id và khôi phục polling.
>
> Hành vi hiện tại: Material hiển thị "Đang xử lý" cho đến khi người dùng rời trang
> hoặc worker hoàn thành (sau đó người dùng cần reload thủ công để thấy "Đã xử lý").
