from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"))

    # Связи
    creator = relationship("User", back_populates="tasks")
    responses = relationship("Response", back_populates="task")

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    image_path = Column(String)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))

    # Связи
    author = relationship("User", back_populates="responses")
    task = relationship("Task", back_populates="responses")
    votes = relationship("Vote", back_populates="response")

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    response_id = Column(Integer, ForeignKey("responses.id"))

    # Связи
    user = relationship("User", back_populates="votes")
    response = relationship("Response", back_populates="votes")

# Дополнительная модель для хранения топовых работ 
class TopResponse(Base):
    __tablename__ = "top_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"))
    score = Column(Float, default=0.0)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь
    response = relationship("Response")