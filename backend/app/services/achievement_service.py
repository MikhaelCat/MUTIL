from sqlalchemy.orm import Session
from app.models.models import User, Achievement, UserAchievement

def check_and_award_achievements(db: Session, user_id: int, action: str, **kwargs):
    """Проверяет и выдает достижения пользователю."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    # Пример проверки достижений
    if action == "create_task" and user.tasks:
        task_count = len(user.tasks)
        if task_count == 1:
            award_achievement(db, user_id, "first_task")
        elif task_count == 10:
            award_achievement(db, user_id, "ten_tasks")

def award_achievement(db: Session, user_id: int, achievement_name: str):
    """Выдает достижение пользователю."""
    achievement = db.query(Achievement).filter(Achievement.name == achievement_name).first()
    if achievement:
        # Проверяем, не было ли уже выдано это достижение
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id
        ).first()
        
        if not existing:
            user_achievement = UserAchievement(user_id=user_id, achievement_id=achievement.id)
            db.add(user_achievement)
            db.commit()
            # Отправляем уведомление пользователю
            # send_notification(user_id, f"Поздравляем! Вы получили достижение: {achievement.name}")    