# AI/RAG Pipeline

Tài liệu mô tả luồng AI trong `backend/app/ai/`. LLM và embedding đều dùng
**Gemini API** (`google-genai`), vector store dùng **Qdrant**.

## 1. Toàn cảnh

```txt
Giai đoạn A - Xử lý học liệu (worker: material_worker.process_material)

  PDF/TXT
  -> extraction        app/ai/extraction/pdf_extractor.py
  -> cleaning          app/ai/extraction/text_cleaner.py
  -> chunking          app/ai/chunking/chunker.py        (parent-child, cắt theo mốc câu)
  -> embedding         app/ai/embedding/embedder.py      (RETRIEVAL_DOCUMENT)
  -> Qdrant upsert     app/ai/vector_store/qdrant_store.py  (collection material_chunks)

Giai đoạn B - Sinh câu hỏi (worker: question_worker.process_question_generation_job)

  query
  -> retrieval         app/ai/retrieval/retriever.py     (multi-query + diversity + fallback)
  -> generation        app/ai/generation/question_generator.py  (Gemini JSON mode + sinh bù)
  -> parsing           app/ai/generation/output_parser.py       (lenient, cứu từng câu)
  -> refine nhãn       app/ai/validation/bloom_classifier.py
  -> validate luật     app/ai/validation/question_validator.py
  -> dedupe trong lô   app/ai/validation/duplicate_detector.py
  -> LLM judge         app/ai/validation/llm_judge.py    (tuỳ chọn, ENABLE_LLM_JUDGE)
  -> dedupe ngân hàng  app/ai/validation/duplicate_detector.py  (collection question_vectors)
  -> draft / review_required
```

Điểm vào duy nhất của giai đoạn B là
`app.ai.pipeline.generate_questions_for_material(...)`. Worker chỉ còn nhiệm vụ
đọc/ghi DB và cập nhật trạng thái job.

## 2. Cấu trúc thư mục

| Thư mục            | Vai trò                                                            |
| ------------------ | ------------------------------------------------------------------ |
| `ai/llm/`          | Provider LLM: `GeminiLLMProvider` (JSON mode, retry) và `FakeLLMProvider` |
| `ai/prompts/`      | File prompt `.txt` + registry có version (`load_prompt`, `render_prompt`) |
| `ai/extraction/`   | Adapter trích xuất và làm sạch văn bản                              |
| `ai/chunking/`     | Chia parent-child chunk                                             |
| `ai/embedding/`    | `GeminiEmbedder` và `FakeDeterministicEmbedder`                     |
| `ai/vector_store/` | Qdrant: 2 collection, payload index, scroll, delete                 |
| `ai/retrieval/`    | Truy hồi context (đơn truy vấn và đa truy vấn có đa dạng hoá)        |
| `ai/generation/`   | Dựng prompt, gọi LLM, parse output                                  |
| `ai/validation/`   | Luật, Bloom/difficulty, trùng lặp, LLM judge                        |
| `ai/pipeline.py`   | Orchestrator giai đoạn B                                            |

Mọi module con đều có `__init__.py`, import theo một chiều từ trên xuống dưới
theo thứ tự trong sơ đồ, nên không có vòng import.

## 3. Những quyết định thiết kế đáng chú ý

**Gemini chạy JSON mode.** `question_generator` gửi kèm `response_schema`
(`MCQ_RESPONSE_SCHEMA`) và `response_mime_type=application/json`. Model trả
JSON đúng cấu trúc ngay lần đầu, không phải bóc code fence hay retry vì sai
format. Parser vẫn giữ cơ chế bóc code fence và tìm khối JSON để phòng trường
hợp model cũ hoặc provider khác.

**Retry có backoff.** `GeminiLLMProvider` retry với backoff luỹ thừa + jitter
cho 429/5xx/timeout - nhóm lỗi hay gặp nhất với API key free tier. Lỗi 4xx
khác và nội dung bị chặn bởi safety thì fail ngay vì retry vô ích.

**Parse cứu vãn từng câu.** `parse_questions_lenient` giữ các câu hợp lệ và bỏ
câu hỏng. Trước đây một câu sai định dạng làm hỏng cả job.

**Sinh bù.** Nếu sau khi lọc còn thiếu so với `number_of_questions`, generator
gọi tiếp (tối đa `GENERATION_MAX_ATTEMPTS` lượt) và đính kèm danh sách câu đã
có vào prompt để model không lặp ý.

**Retrieval đa truy vấn + đa dạng hoá.** `retrieve_diverse_context` chạy truy
vấn gốc cùng vài biến thể theo khía cạnh, gộp kết quả theo `chunk_id`, rồi
chọn luân phiên qua từng `parent_id` và cắt theo ngân sách ký tự. Điều này
tránh việc cả 5 câu hỏi cùng rút ra từ một đoạn văn.

**Fallback khi retrieval rỗng.** Nếu similarity không trả về gì (Qdrant chưa
index xong, hoặc đang chạy embedding giả), pipeline quét thẳng chunk theo
`material_id`. Fallback lỗi thì chỉ ghi log, không làm hỏng job.

**Embedding phân biệt document và query.** `RETRIEVAL_DOCUMENT` khi index,
`RETRIEVAL_QUERY` khi tìm kiếm - đây là yếu tố ảnh hưởng lớn tới điểm
similarity của `gemini-embedding-001`.

**Hai lớp chống trùng.** So khớp text đã chuẩn hoá trong cùng lô (luôn chạy),
và so vector với collection `question_vectors` (chỉ chạy khi dùng embedding
thật, vì với embedding giả điểm similarity vô nghĩa).

**Trạng thái câu hỏi.** `draft` khi không có cảnh báo nào; `review_required`
khi có cảnh báo từ luật, từ judge, hoặc nghi trùng. Câu hỏi có `errors` bị loại
hẳn và ghi vào `outcome.dropped`.

## 4. Cấu hình

Xem `.env.example` cho danh sách đầy đủ. Các biến ảnh hưởng chất lượng nhiều nhất:

| Biến                     | Mặc định           | Ý nghĩa                                            |
| ------------------------ | ------------------ | -------------------------------------------------- |
| `EMBEDDING_PROVIDER`     | `fake`             | Đặt `gemini` để retrieval có ý nghĩa thật          |
| `LLM_MODEL`              | `gemini-2.5-flash` | Model sinh câu hỏi                                  |
| `LLM_THINKING_BUDGET`    | `0`                | `-1` để Gemini tự suy luận sâu hơn (chậm/đắt hơn)   |
| `RAG_TOP_K`              | `8`                | Số chunk đưa vào prompt                             |
| `GENERATION_MAX_ATTEMPTS`| `3`                | Số lượt sinh bù tối đa                              |
| `ENABLE_LLM_JUDGE`       | `false`            | Bật judge ngữ nghĩa (gấp đôi số lần gọi API)        |

> Đổi `EMBEDDING_PROVIDER` giữa `fake` và `gemini` làm vector cũ trong Qdrant
> không còn so sánh được với vector mới. Sau khi đổi phải xử lý lại
> (`POST /api/v1/materials/{id}/process`) toàn bộ học liệu.

## 5. Chạy không có GEMINI_API_KEY

Khi thiếu key và `LLM_ALLOW_FAKE_FALLBACK=true`, generator dùng
`FakeLLMProvider`: sinh JSON đúng schema nên toàn bộ pipeline phía sau chạy y
hệt luồng thật, phù hợp cho unit test và demo offline. Log sẽ ghi cảnh báo rõ
rằng câu hỏi là dữ liệu giả lập. Đặt `LLM_ALLOW_FAKE_FALLBACK=false` ở môi
trường thật để job fail thay vì âm thầm sinh câu hỏi giả.

## 6. Test

```bash
python -m pytest backend/tests -q
```

Unit test không gọi Gemini và không cần Qdrant thật: provider LLM, embedder,
vector store và retrieval đều được mock.
