from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.schemas.schemas import Response
from app.models.models import Response as ResponseModel
from sqlalchemy import func

router = APIRouter()

@router.get("/top", response_model=List[Response])
def get_top_responses(limit: int = 10, db: Session = Depends(get_db)):
    """Получает топ ответов по количеству голосов."""
    # Подсчитываеt coчество голосов для каждого ответа
    vote_counts = db.query(
        ResponseModel.id,
        func.count(ResponseModel.votes).label('vote_count')
    ).join(ResponseModel.votes).group_by(ResponseModel.id).subquery()
    
    # Получаеt top ветов
    top_responses = db.query(ResponseModel).join(
        vote_counts, ResponseModel.id == vote_counts.c.id
    ).order_by(vote_counts.c.vote_count.desc()).limit(limit).all()
    
    return top_responses

@router.get("/recent", response_model=List[Response])
def get_recent_responses(limit: int = 10, db: Session = Depends(get_db)):
    """Получает последние добавленные ответы."""
    responses = db.query(ResponseModel).order_by(
        ResponseModel.created_at.desc()
    ).limit(limit).all()
    
    return responses