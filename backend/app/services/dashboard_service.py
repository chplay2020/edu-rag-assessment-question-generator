from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.course import Course
from app.models.material import Material, Job
from app.models.question import Question, QuestionValidationResult
from app.schemas.dashboard_schema import DashboardSummaryResponse

def get_dashboard_summary(db: Session, user_id: int, role: str) -> DashboardSummaryResponse:
    course_query = db.query(Course)
    material_query = db.query(Material)
    job_query = db.query(Job)
    question_query = db.query(Question)

    if role != "admin":
        course_query = course_query.filter(Course.created_by == user_id)
        material_query = material_query.join(Course, Material.course_id == Course.id).filter(Course.created_by == user_id)
        job_query = job_query.join(Material, Job.material_id == Material.id).join(Course, Material.course_id == Course.id).filter(Course.created_by == user_id)
        question_query = question_query.join(Course, Question.course_id == Course.id).filter(Course.created_by == user_id)

    total_courses = course_query.count()
    total_materials = material_query.count()
    total_jobs = job_query.count()
    total_generated_questions = question_query.count()
    
    total_approved_questions = question_query.filter(Question.status == "approved").count()
    total_rejected_questions = question_query.filter(Question.status == "rejected").count()

    # Calculate validation avg score using LLM judge scores
    score_query = db.query(QuestionValidationResult.score)\
        .join(Question, QuestionValidationResult.question_id == Question.id)

    if role != "admin":
        score_query = score_query.join(Course, Question.course_id == Course.id).filter(Course.created_by == user_id)

    score_query = score_query.filter(QuestionValidationResult.validator_type == 'llm_judge')
    
    results = score_query.all()
    
    total_score = 0.0
    count = 0
    for (score_dict,) in results:
        if score_dict:
            total_score += sum(score_dict.values())
            count += len(score_dict)

    validation_avg_score = round(total_score / count, 2) if count > 0 else 0.0

    # Calculate charts data
    diff_query = db.query(Question.difficulty, func.count(Question.id)).group_by(Question.difficulty)
    bloom_query = db.query(Question.bloom_level, func.count(Question.id)).group_by(Question.bloom_level)
    status_query = db.query(Question.status, func.count(Question.id)).group_by(Question.status)

    if role != "admin":
        diff_query = diff_query.join(Course, Question.course_id == Course.id).filter(Course.created_by == user_id)
        bloom_query = bloom_query.join(Course, Question.course_id == Course.id).filter(Course.created_by == user_id)
        status_query = status_query.join(Course, Question.course_id == Course.id).filter(Course.created_by == user_id)

    questions_by_difficulty = [{"name": str(k or "unknown"), "value": v} for k, v in diff_query.all()]
    questions_by_bloom = [{"name": str(k or "unknown"), "value": v} for k, v in bloom_query.all()]
    questions_by_status = [{"name": str(k or "unknown"), "value": v} for k, v in status_query.all()]

    return DashboardSummaryResponse(
        total_courses=total_courses,
        total_materials=total_materials,
        total_jobs=total_jobs,
        total_generated_questions=total_generated_questions,
        total_approved_questions=total_approved_questions,
        total_rejected_questions=total_rejected_questions,
        validation_avg_score=validation_avg_score,
        questions_by_difficulty=questions_by_difficulty,
        questions_by_bloom=questions_by_bloom,
        questions_by_status=questions_by_status
    )
