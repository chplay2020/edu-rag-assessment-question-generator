from app.models.base import Base
from app.models.user import User
from app.models.course import Course
from app.models.material import Material, Chunk, Job
from app.models.question import Question, Option, Review
from app.models.system import Export, AiLog

# Chỉ export Base để Alembic nhận diện tất cả các Models đã được import
__all__ = ["Base", "User", "Course", "Material", "Chunk", "Job", "Question", "Option", "Review", "Export", "AiLog"]
