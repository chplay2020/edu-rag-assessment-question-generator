from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Export(Base):
    __tablename__ = "exports"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    exported_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    format = Column(String, default="excel")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="exports")
    exporter = relationship("User", back_populates="exports")


class AiLog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False) # generate_question, extract_text...
    prompt = Column(Text)
    response = Column(Text)
    model_name = Column(String)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
