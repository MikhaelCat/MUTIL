import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import Vote, Response
from app.schemas.schemas import VoteCreate
from app.core.config import redis_client
from datetime import datetime, timedelta
from sqlalchemy import func

def calculate_hot_score(votes_count: int, created_at: datetime) -> float:
    """Рассчитывает 'горячий' рейтинг как на Reddit."""
    hours_since_creation = (datetime.utcnow() - created_at).total_seconds() / 3600
    return votes_count / ((hours_since_creation + 2) ** 1.8)

def update_response_hot_score_cache(response_id: int, db: Session):
    """Обновляет 'горячий' рейтинг ответа в Redis."""
    response = db.query(Response).filter(Response.id == response_id).first()
    if response:
        votes = db.query(Vote).filter(Vote.response_id == response_id).all()
        votes_count = len(votes)
        hot_score = calculate_hot_score(votes_count, response.created_at)
        redis_client.hset(f"response:{response_id}", "hot_score", hot_score)
        redis_client.hset(f"response:{response_id}", "votes_count", votes_count)

def create_vote(db: Session, vote: VoteCreate, user_id: int) -> Vote:
    """Создает новый голос."""
    db_vote = Vote(**vote.model_dump(), user_id=user_id)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    update_response_score_cache(vote.response_id, db)
    return db_vote

def get_vote(db: Session, vote_id: int) -> Optional[Vote]:
    """Получает голос по ID."""
    return db.query(Vote).filter(Vote.id == vote_id).first()

def get_votes_for_response(db: Session, response_id: int) -> list[Vote]:
    """Получает все голоса для ответа."""
    return db.query(Vote).filter(Vote.response_id == response_id).all()

def update_response_score_cache(response_id: int, db: Session):
    """Обновляет рейтинг ответа в Redis."""
    response = db.query(Response).filter(Response.id == response_id).first()
    if response:
        votes = db.query(Vote).filter(Vote.response_id == response_id).all()
        score = sum(vote.value for vote in votes)
        redis_client.hset(f"response:{response_id}", "score", score)
        redis_client.hset(f"response:{response_id}", "votes_count", len(votes))
        update_top_responses_cache(db)

def update_top_responses_cache(db: Session, limit: int = 10):
    """Обновляет кэш топовых ответов."""
    # Получаем топ ответов из БД
    from sqlalchemy import func
    vote_counts = db.query(
        Response.id,
        func.count(Vote.id).label('vote_count')
    ).join(Vote, Response.id == Vote.response_id).group_by(Response.id).order_by(func.count(Vote.id).desc()).limit(limit).all()
    
    # Преобразуем в список ID
    top_ids = [str(item[0]) for item in vote_counts]
    
    # Сохраняем в Redis
    redis_client.delete("top_responses")
    if top_ids:
        redis_client.lpush("top_responses", *top_ids)