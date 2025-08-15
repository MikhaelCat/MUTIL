from sqlalchemy.orm import Session
from app.models.models import User

XP_VALUES = {
    "create_task": 10,
    "create_response": 15,
    "receive_vote": 5,
    "give_vote": 2,
    "create_comment": 3,
}

def award_xp(db: Session, user_id: int, action: str, amount: int = None):
    """Начисляет XP пользователю."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    xp_to_award = amount if amount is not None else XP_VALUES.get(action, 0)
    user.experience_points += xp_to_award
    
    # Проверяем повышение уровня
    new_level = calculate_level(user.experience_points)
    if new_level > user.level:
        user.level = new_level
    
    db.commit()

def calculate_level(xp: int) -> int:
    """Рассчитывает уровень на основе XP."""
    import math
    return int(math.sqrt(xp / 100)) + 1