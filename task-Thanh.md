# README AI/RAG Tasks

## 1. Tổng quan

Phần AI/RAG của backend trong project `edu-rag-assessment-question-generator` dùng để xử lý học liệu PDF/TXT và sinh câu hỏi trắc nghiệm MCQ cho giảng viên review.

Luồng mục tiêu:

```txt
PDF/TXT
-> extract text
-> clean text
-> chunking
-> embedding
-> Qdrant retrieval
-> Gemini/Fake LLM generate MCQ
-> parse JSON
-> validate
-> save draft/review_required questions
```

Hiện tại core AI/RAG đã hoàn thành ở mức **MVP + unit test**. Câu hỏi AI sinh ra được lưu ở trạng thái `draft` hoặc `review_required`, không tự động `approved`.

Lưu ý: Unit tests đang dùng fake/mock cho Gemini, Qdrant và một số luồng worker. Chưa có automated integration test chứng minh toàn bộ API flow chạy thật với DB + Qdrant + Gemini.

## 2. Module chính

| Nhóm                        | File/module chính                                               | Trạng thái |
| --------------------------- | --------------------------------------------------------------- | ---------- |
| Extraction                  | `text_extraction_service.py`, `ai/extraction/pdf_extractor.py`  | Done       |
| Text cleaning               | `text_cleaning_service.py`, `ai/extraction/text_cleaner.py`     | Done       |
| Chunking                    | `ai/chunking/chunker.py`                                        | Done       |
| Embedding                   | `ai/embedding/embedder.py`                                      | Done (MVP) |
| Qdrant store                | `ai/vector_store/qdrant_store.py`                               | Done (MVP) |
| Retrieval                   | `ai/retrieval/retriever.py`                                     | Done (MVP) |
| Prompt + Parser             | `ai/prompts/generate_mcq.txt`, `ai/generation/output_parser.py` | Done       |
| Gemini/Fake generator       | `ai/generation/question_generator.py`                           | Done (MVP) |
| Validation                  | `ai/validation/question_validator.py`                           | Done       |
| Bloom/Difficulty classifier | `ai/validation/bloom_classifier.py`                             | Done (MVP) |
| Duplicate detector          | `ai/validation/duplicate_detector.py`                           | Done (MVP) |
| Workers                     | `workers/material_worker.py`, `workers/question_worker.py`      | Done (MVP) |

## 3. Trạng thái task AI

| Task | Nội dung                                      | Trạng thái  |
| ---- | --------------------------------------------- | ----------- |
| T023 | PDF/TXT text extraction service               | Done        |
| T024 | Text cleaning service                         | Done        |
| T025 | Chunking service                              | Done        |
| T026 | Embedding service                             | Done (MVP)  |
| T027 | Lưu chunks + embedding vào Qdrant             | Done (MVP)  |
| T031 | Retrieval service theo material/course        | Done (MVP)  |
| T032 | Prompt MCQ JSON v1                            | Done        |
| T033 | LLM generator service bằng Gemini             | Done (MVP)  |
| T041 | Rule-based validation                         | Done        |
| T042 | LLM validation prompt                         | Partial     |
| T043 | Bloom classifier/refiner                      | Done (MVP)  |
| T044 | Difficulty classifier/refiner                 | Done (MVP)  |
| T045 | Duplicate detection bằng embedding similarity | Done (MVP)  |
| T040 | Checkpoint demo PDF -> 5 MCQ                  | Blocked     |
| T030 | Test pipeline với 2 PDF mẫu                   | Not started |
| T049 | Prompt versioning                             | Not started |
| T069 | Duplicate against full question bank          | Not started |
| T073 | Bộ tài liệu mẫu đánh giá                      | Not started |
| T074 | Human evaluation rubric sheet                 | Not started |
| T075 | So sánh RAG vs không RAG                      | Not started |

Ghi chú:

* `Done`: đã có code thật và test pass.
* `Done (MVP)`: đã chạy được ở mức MVP/unit test, nhưng còn thiếu provider production hoặc integration test thật.
* `Partial`: đã có một phần nhưng chưa đủ service/test để xác nhận hoàn thành.
* `Blocked`: có code nền nhưng chưa verify được do thiếu môi trường Docker/API thật.

## 4. Kết quả kiểm thử

Kết quả kiểm thử hiện tại:

```txt
AI pipeline unit tests: 60 passed
Full backend tests: 81 passed
```

Unit tests không gọi Gemini API thật và không yêu cầu Qdrant thật.

Các test file chính:

```bash
python -m pytest backend/tests/test_ai_extraction_adapter.py backend/tests/test_ai_text_cleaner_adapter.py backend/tests/test_ai_chunker.py backend/tests/test_material_processing_worker.py backend/tests/test_ai_embedder.py backend/tests/test_ai_qdrant_store.py backend/tests/test_ai_retriever.py backend/tests/test_ai_output_parser.py backend/tests/test_ai_question_generator.py backend/tests/test_ai_question_validator.py backend/tests/test_ai_bloom_classifier.py backend/tests/test_ai_duplicate_detector.py backend/tests/test_question_generation_worker.py
```

Chạy toàn bộ backend tests:

```bash
python -m pytest backend/tests -v
```

Một số test file còn rỗng:

```txt
backend/tests/test_auth.py
backend/tests/test_export.py
backend/tests/test_question_generation.py
```

## 5. Cách cài dependencies

Từ root project:

```bash
cd ~/src/edu-rag-assessment-question-generator
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Kiểm tra package chính:

```bash
python -c "import fastapi; import sqlalchemy; import fitz; print('Backend packages OK')"
python -c "import qdrant_client; print('Qdrant OK')"
python -c "from google import genai; print('Gemini package OK')"
```

## 6. Cấu hình môi trường

Các biến chính:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=edu_rag_db

UPLOAD_DIR=storage/uploads
PROCESSED_DIR=storage/processed

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_MATERIAL_COLLECTION=material_chunks
QDRANT_QUESTION_COLLECTION=question_vectors

EMBEDDING_PROVIDER=fake
EMBEDDING_MODEL=fake-deterministic-embedding
EMBEDDING_DIMENSION=768

LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_api_key_here
```

Không commit `.env` thật hoặc Gemini API key lên GitHub.

## 7. Cách chạy backend và services

Chạy DB + Qdrant:

```bash
docker compose up -d db qdrant
```

Chạy toàn bộ stack:

```bash
docker compose up -d --build
```

Chạy backend riêng:

```bash
cd backend
uvicorn app.main:app --reload
```

Mở Swagger:

```txt
http://localhost:8000/docs
```

Qdrant dashboard:

```txt
http://localhost:6333/dashboard
```

## 8. API flow cần test thủ công

Flow demo cần verify trong môi trường có Docker đầy đủ:

```txt
login/register
-> create course
-> upload TXT/PDF material
-> process material
-> wait material processed
-> generate questions
-> wait job done
-> get questions by material
```

Endpoints chính:

```txt
POST /api/v1/materials/upload
GET /api/v1/materials/{material_id}
POST /api/v1/materials/{material_id}/process
POST /api/v1/jobs/material/{material_id}/generate-questions
GET /api/v1/jobs/{job_id}
GET /api/v1/questions/material/{material_id}
```

Kết quả mong đợi:

```txt
Material: uploaded -> processing -> processed
Job: pending/running -> done
Question: draft hoặc review_required
```

Mỗi câu hỏi cần có 4 options và đúng 1 option `is_correct=true`.

## 9. Rủi ro còn lại

* Chưa có automated API end-to-end test cho flow `upload -> process -> Qdrant -> retrieval -> generate -> save questions`.
* Qdrant service chưa được verify trong môi trường test trước đó do thiếu Docker.
* Gemini provider đã có, nhưng unit test không gọi Gemini thật.
* Embedding hiện là fake deterministic provider, chưa có production embedding provider.
* Duplicate detector chưa so sánh với toàn bộ question bank.
* Export route vẫn còn mock.
* Còn một số warning từ Pydantic/SQLAlchemy/passlib.

## 10. TODO tiếp theo

Ưu tiên làm tiếp:

1. Chạy manual API demo với Docker thật.
2. Verify T040: PDF/TXT -> 5 MCQ -> lưu DB.
3. Thêm integration test với Qdrant thật.
4. Thêm controlled Gemini integration smoke test.
5. Thêm production embedding provider nếu cần.
6. Implement duplicate detection against full question bank.
7. Thêm prompt versioning.
8. Chuẩn bị 2 PDF mẫu cho T030.
9. Thêm evaluation dataset, rubric và so sánh RAG vs non-RAG.

## 11. Kết luận

Core AI/RAG MVP đã hoàn thành ở mức unit test.

Có thể đánh dấu:

```txt
Done:
T023, T024, T025, T032, T041

Done (MVP):
T026, T027, T031, T033, T043, T044, T045
```

Chưa nên đánh dấu hoàn thành tuyệt đối cho T040/T030/evaluation tasks cho đến khi có manual/API integration test với môi trường Docker + DB + Qdrant đầy đủ.
