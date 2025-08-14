from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from app.api.deps import get_db
from app.core.config import redis_client
from app.models.models import Response as ResponseModel

router = APIRouter()

@router.get("/top-responses")
def get_cached_top_responses(limit: int = 10, db: Session = Depends(get_db)):
    """Получает топ ответов из кэша Redis."""
    top_ids = redis_client.lrange("top_responses", 0, limit - 1)
    
    if not top_ids:
        # Если кэш пуст, возвращаем пустой список
        return []
    
    # Получаем данные ответов из БД
    responses = db.query(ResponseModel).filter(
        ResponseModel.id.in_([int(id_) for id_ in top_ids])
    ).all()
    
    # Сортируем по порядку из Redis
    response_dict = {r.id: r for r in responses}
    sorted_responses = [response_dict[int(id_)] for id_ in top_ids if int(id_) in response_dict]
    
    # Добавляем рейтинг из Redis
    result = []
    for response in sorted_responses:
        score = redis_client.hget(f"response:{response.id}", "score") or 0
        votes_count = redis_client.hget(f"response:{response.id}", "votes_count") or 0
        result.append({
            "id": response.id,
            "text": response.text,
            "image_path": response.image_path,
            "created_at": response.created_at,
            "author_id": response.author_id,
            "task_id": response.task_id,
            "score": int(score),
            "votes_count": int(votes_count)
        })
    
    return result

@router.get("/stats")
def get_system_stats():
    """Получает статистику системы."""
    stats = {
        "redis_info": redis_client.info(),
        "redis_keys": redis_client.keys("*")
    }
    return stats

@router.post("/clear-cache")
def clear_cache():
    """Очищает кэш Redis."""
    redis_client.flushdb()
    return {"message": "Cache cleared"}