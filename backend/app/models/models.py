from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import Session

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="tasks")
    responses = relationship("Response", back_populates="task")
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    response_id = Column(Integer, ForeignKey("responses.id"))

    author = relationship("User", back_populates="comments")
    response = relationship("Response", back_populates="comments")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    image_path = Column(String)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))

    author = relationship("User", back_populates="responses")
    task = relationship("Task", back_populates="responses")
    votes = relationship("Vote", back_populates="response")
    comments = relationship("Comment", back_populates="response")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    experience_points = Column(Integer, default=0)
    level = Column(Integer, default=1)

    tasks = relationship("Task", back_populates="creator")
    responses = relationship("Response", back_populates="author")
    votes = relationship("Vote", back_populates="user")
    comments = relationship("Comment", back_populates="author")
    user_achievements = relationship("UserAchievement", back_populates="user")

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    response_id = Column(Integer, ForeignKey("responses.id"))

    user = relationship("User", back_populates="votes")
    response = relationship("Response", back_populates="votes")


class TopResponse(Base):
    __tablename__ = "top_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"))
    score = Column(Float, default=0.0)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    response = relationship("Response")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    reason = Column(String)  
    description = Column(Text) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")  

    reporter = relationship("User")
    response = relationship("Response")
    task = relationship("Task")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    points = Column(Integer, default=0)
    icon = Column(String)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    achievement = relationship("Achievement")

# Пример достижений
ACHIEVEMENTS = [
    {"name": "Первый шаг", "description": "Создайте первое задание", "points": 10},
    {"name": "Креативщик", "description": "Создайте 10 заданий", "points": 50},
    {"name": "Критик", "description": "Проголосуйте за 50 работ", "points": 30},
    {"name": "Популярность", "description": "Получите 100 голосов за свои работы", "points": 100},
]


def update_user_experience(db: Session, user_id: int, points: int):
    """Обновляет опыт пользователя и уровень."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.experience_points += points
        new_level = user.experience_points // 100 + 1
        if new_level > user.level:
            user.level = new_level
        db.commit()

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")


class TaskTag(Base):
    __tablename__ = "task_tags"
    
    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement")

#система подписок
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subscriber = relationship("User", foreign_keys=[subscriber_id])
    target_user = relationship("User", foreign_keys=[target_user_id])

#Система бейджей
class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    icon = Column(String)  

class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

    badge = relationship("Badge")

