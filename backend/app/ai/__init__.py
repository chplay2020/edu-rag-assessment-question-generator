"""Lớp AI/RAG của EduRAG.

Luồng chuẩn (xem `app/ai/pipeline.py`):

    PDF/TXT
    -> extraction        (app.ai.extraction)
    -> cleaning          (app.ai.extraction.text_cleaner)
    -> chunking          (app.ai.chunking)
    -> embedding         (app.ai.embedding)      Gemini | fake deterministic
    -> Qdrant index      (app.ai.vector_store)
    -> retrieval         (app.ai.retrieval)      multi-query + diversity
    -> generation        (app.ai.generation)     Gemini JSON mode + retry/top-up
    -> parsing           (app.ai.generation.output_parser)
    -> validation        (app.ai.validation)     rule-based + Bloom refine + LLM judge
    -> deduplication     (app.ai.validation.duplicate_detector)
    -> draft/review_required questions

Module con chỉ import "xuống dưới" theo thứ tự trên để tránh vòng import.
`app.ai.pipeline` là điểm vào duy nhất mà worker nên dùng.
"""

__all__: list[str] = []
