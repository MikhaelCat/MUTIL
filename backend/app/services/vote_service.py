import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import Vote, Response
from app.schemas.schemas import VoteCreate
from app.core.config import redis_client

def create_vote(db: Session, vote: VoteCreate, user_id: int) -> Vote:
    """Создает новый голос."""
    db_vote = Vote(**vote.model_dump(), user_id=user_id)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    
    # Обновляем рейтинг ответа в Redis
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
        
        # Сохраняем в Redis
        redis_client.hset(f"response:{response_id}", "score", score)
        redis_client.hset(f"response:{response_id}", "votes_count", len(votes))
        
        # Обновляем список топовых ответов
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