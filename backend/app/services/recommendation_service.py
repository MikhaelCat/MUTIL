from sqlalchemy.orm import Session
from app.models.models import Task, Response, User
from typing import List

def get_recommended_tasks(db: Session, user_id: int, limit: int = 5) -> List[Task]:
    """Получает рекомендованные задания для пользователя."""
    recommended = db.query(Task).join(Response).group_by(Task.id).order_by(
        func.count(Response.id).desc()
    ).limit(limit).all()
    
    return recommended

def get_similar_responses(db: Session, response_id: int, limit: int = 5) -> List[Response]:
    """Получает похожие ответы."""
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        return []
    
    similar = db.query(Response).filter(
        Response.task_id == response.task_id,
        Response.id != response_id
    ).limit(limit).all()
    
    return similar