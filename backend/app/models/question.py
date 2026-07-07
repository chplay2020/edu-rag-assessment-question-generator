from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    difficulty = Column(String, default="medium") # easy, medium, hard
    bloom_level = Column(String) 
    question_type = Column(String, default="multiple_choice") 
    explanation = Column(Text)
    status = Column(String, default="pending") # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    material = relationship("Material", back_populates="questions")
    course = relationship("Course", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="question", cascade="all, delete-orphan")


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    question = relationship("Question", back_populates="options")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False) # approved, rejected
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    question = relationship("Question", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
