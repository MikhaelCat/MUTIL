from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.models import User, Task, Response, Vote

router = APIRouter()

@router.get("/stats")
def get_platform_stats(db: Session = Depends(get_db)):
    """Получает статистику платформы."""
    stats = {
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_tasks": db.query(func.count(Task.id)).scalar(),
        "total_responses": db.query(func.count(Response.id)).scalar(),
        "total_votes": db.query(func.count(Vote.id)).scalar(),
        "active_users_24h": db.query(func.count(User.id)).filter(
            User.created_at >= func.now() - timedelta(hours=24)
        ).scalar(),
    }
    return stats