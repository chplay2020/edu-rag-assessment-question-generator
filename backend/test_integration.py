import sys
from app.core.database import SessionLocal
from app.models.material import Material, Job, Chunk; from app.models.course import Course
from app.models.user import User
from app.models.system import AiLog
from app.workers.question_worker import process_question_generation_job

def test_db():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        user = User(email="test@test.com", hashed_password="xxx", full_name="Test", role="lecturer")
        db.add(user)
        db.commit()

    course = db.query(Course).first()
    if not course:
        course = Course(title="Test Course", description="", author_id=user.id)
        db.add(course)
        db.commit()

    material = Material(title="Test Material", file_path="test.pdf", course_id=course.id, uploaded_by=user.id, status="processed")
    db.add(material)
    db.commit()
    
    chunk = Chunk(material_id=material.id, chunk_index=0, content="Fake content")
    db.add(chunk)
    db.commit()

    job = Job(material_id=material.id, task_type="generate_questions", config={"number_of_questions": 1, "difficulty": "medium", "language": "vi"})
    db.add(job)
    db.commit()

    try:
        process_question_generation_job(job.id)
    except Exception as e:
        print(f"FAILED: {e}")
        db.close()
        sys.exit(1)

    # Verify AiLog
    db.refresh(job)
    print("Logs created:", len(job.ai_logs))
    if len(job.ai_logs) == 0:
        print("FAILED: No AiLog created!")
        sys.exit(1)
        
    for log in job.ai_logs:
        print(f"Action: {log.action}")
        print(f"Tokens: P={log.prompt_tokens}, O={log.output_tokens}, T={log.total_tokens}")
        print(f"Cost: {log.cost_estimate}, Latency: {log.latency_ms}, Error: {log.error}")

    db.close()
    print("SUCCESS")

if __name__ == "__main__":
    test_db()
