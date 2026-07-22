from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.models.base import Base
# Tạm thời mock Vector type, sau này cài pgvector thì sẽ import từ pgvector.sqlalchemy
from sqlalchemy.types import UserDefinedType

class MockVector(UserDefinedType):
    def get_col_spec(self, **kw):
        return "VECTOR(768)" # Tùy theo mô hình embedding

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="processing") # processing, done, failed
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="materials")
    uploader = relationship("User", back_populates="materials")
    chunks = relationship("Chunk", back_populates="material", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="material", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="material", cascade="all, delete-orphan")

    @property
    def file_url(self) -> str:
        # Đường dẫn tĩnh phục vụ frontend 
        return f"/{self.file_path}".replace("\\", "/")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
     
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    material = relationship("Material", back_populates="chunks")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    task_type = Column(String, nullable=False) # extract, generate
    status = Column(String, default="pending") # pending, running, success, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    material = relationship("Material", back_populates="jobs")
