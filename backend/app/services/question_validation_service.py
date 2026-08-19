from typing import Any
from sqlalchemy.orm import Session
from app.models.question import Question, QuestionValidationResult
from app.ai.validation.question_validator import validate_question
from app.ai.validation.duplicate_detector import detect_duplicate_question

def revalidate_question(db: Session, question: Question) -> None:
    """
    Chạy lại quá trình kiểm định (rule-based và duplicate check) cho câu hỏi sau khi được chỉnh sửa.
    Cập nhật lại kết quả vào bảng question_validation_results.
    """
    # 1. Chuyển đổi thành dạng dict để validator dùng
    correct_option = next((opt for opt in question.options if opt.is_correct), None)
    question_dict: dict[str, Any] = {
        "question_text": question.content,
        "options": [{"text": o.content, "is_correct": o.is_correct} for o in question.options],
        "correct_answer": correct_option.content if correct_option else "",
        "difficulty": question.difficulty,
        "bloom_level": question.bloom_level,
        "explanation": question.explanation,
        "source_chunk_ids": question.source_chunk_ids
    }
    
    # 2. Chạy Rule-based validation
    validation_result = validate_question(question_dict)
    
    # 3. Chạy Duplicate detection (bỏ qua chính câu hỏi này trong Qdrant)
    is_duplicate, duplicate_warnings = False, []
    if question.content:
        dup_result = detect_duplicate_question(
            question.content,
            material_id=question.material_id,
            course_id=question.course_id,
            exclude_question_id=question.id
        )
        is_duplicate = dup_result.is_duplicate
        duplicate_warnings = dup_result.warnings
    
    warnings = list(validation_result.warnings)
    if duplicate_warnings:
        warnings.extend(duplicate_warnings)
    if is_duplicate:
        warnings.append("Có thể trùng với câu hỏi đã có trong ngân hàng câu hỏi.")
    
    # 4. Cập nhật kết quả vào DB
    # Xóa kết quả rule_based cũ
    db.query(QuestionValidationResult).filter(
        QuestionValidationResult.question_id == question.id,
        QuestionValidationResult.validator_type == "rule_based"
    ).delete()
    
    # Thêm kết quả rule_based mới
    new_result = QuestionValidationResult(
        question_id=question.id,
        validator_type="rule_based",
        score=validation_result.scores,
        warnings=warnings
    )
    db.add(new_result)
    
    # Cập nhật status của câu hỏi nếu cần
    if not validation_result.is_valid or warnings:
        question.status = "review_required"
    
    # Không commit ở đây, để API route commit chung với transaction update câu hỏi
