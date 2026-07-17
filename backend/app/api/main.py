from fastapi import APIRouter
from app.api.routes import auth, courses, materials, jobs, questions, exports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
