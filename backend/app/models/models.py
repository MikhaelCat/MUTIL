from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# --- Модели ---
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

    # Связи
    tasks = relationship("Task", back_populates="creator")
    responses = relationship("Response", back_populates="author")
    votes = relationship("Vote", back_populates="user")
    comments = relationship("Comment", back_populates="author")
    user_achievements = relationship("UserAchievement", back_populates="user")
    # Для подписок
    subscriptions_as_subscriber = relationship("Subscription", foreign_keys="Subscription.subscriber_id", back_populates="subscriber")
    subscriptions_as_target = relationship("Subscription", foreign_keys="Subscription.target_user_id", back_populates="target_user")
    # Для бейджей
    user_badges = relationship("UserBadge", back_populates="user")
    # Для отчетов
    reports = relationship("Report", back_populates="reporter")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"))

    # Связи
    creator = relationship("User", back_populates="tasks")
    responses = relationship("Response", back_populates="task")
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")
    # Для отчетов
    reports = relationship("Report", back_populates="task")


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
    comments = relationship("Comment", back_populates="response")
    # Для отчетов
    reports = relationship("Report", back_populates="response")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    response_id = Column(Integer, ForeignKey("responses.id"))

    # Связи
    author = relationship("User", back_populates="comments")
    response = relationship("Response", back_populates="comments")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer)  # Например, 1 для голоса "за", -1 для "против"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    response_id = Column(Integer, ForeignKey("responses.id"))

    # Связи
    user = relationship("User", back_populates="votes")
    response = relationship("Response", back_populates="votes")


class TopResponse(Base):
    __tablename__ = "top_responses"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"))
    score = Column(Float, default=0.0)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь
    response = relationship("Response")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    reason = Column(String)  # Причина жалобы
    description = Column(Text)  # Дополнительное описание
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")  # pending, approved, rejected

    # Связи
    reporter = relationship("User", back_populates="reports")
    response = relationship("Response", back_populates="reports")
    task = relationship("Task", back_populates="reports")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    points = Column(Integer, default=0)
    icon = Column(String)  # Путь к иконке достижения

    # Связи
    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


# Пример достижений (перенес в конец файла, вне классов)
ACHIEVEMENTS = [
    {"name": "Первый шаг", "description": "Создайте первое задание", "points": 10},
    {"name": "Креативщик", "description": "Создайте 10 заданий", "points": 50},
    {"name": "Критик", "description": "Проголосуйте за 50 работ", "points": 30},
    {"name": "Популярность", "description": "Получите 100 голосов за свои работы", "points": 100},
]


# --- Функции (не должны быть внутри классов) ---
# Перенес функцию вне классов и убрал импорт Session из этого файла
# def update_user_experience(db: Session, user_id: int, points: int):
#     """Обновляет опыт пользователя и уровень."""
#     user = db.query(User).filter(User.id == user_id).first()
#     if user:
#         user.experience_points += points
#         new_level = user.experience_points // 100 + 1
#         if new_level > user.level:
#             user.level = new_level
#         db.commit()


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Связи
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")


class TaskTag(Base):
    __tablename__ = "task_tags"

    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


# Система подписок
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    subscriber = relationship("User", foreign_keys=[subscriber_id], back_populates="subscriptions_as_subscriber")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="subscriptions_as_target")


# Система бейджей
class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    icon = Column(String)  # Путь к иконке бейджа

    # Связи
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")
