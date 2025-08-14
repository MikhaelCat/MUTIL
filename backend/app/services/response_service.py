import os
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import Response
from app.schemas.schemas import ResponseCreate, ResponseUpdate
from app.core.config import settings

def create_response(db: Session, response: ResponseCreate, author_id: Optional[int] = None) -> Response:
    """Создает новый ответ."""
    db_response = Response(**response.model_dump(), author_id=author_id)
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

def get_response(db: Session, response_id: int) -> Optional[Response]:
    """Получает ответ по ID."""
    return db.query(Response).filter(Response.id == response_id).first()

def get_responses(db: Session, skip: int = 0, limit: int = 100) -> List[Response]:
    """Получает список ответов."""
    return db.query(Response).offset(skip).limit(limit).all()

def get_responses_for_task(db: Session, task_id: int) -> List[Response]:
    """Получает все ответы для задания."""
    return db.query(Response).filter(Response.task_id == task_id).all()

def update_response(db: Session, response_id: int, response_update: ResponseUpdate) -> Optional[Response]:
    """Обновляет ответ."""
    db_response = db.query(Response).filter(Response.id == response_id).first()
    if db_response:
        for key, value in response_update.model_dump(exclude_unset=True).items():
            setattr(db_response, key, value)
        db.commit()
        db.refresh(db_response)
    return db_response

def delete_response(db: Session, response_id: int) -> bool:
    """Удаляет ответ."""
    db_response = db.query(Response).filter(Response.id == response_id).first()
    if db_response:
        db.delete(db_response)
        db.commit()
        return True
    return False

def save_response_image(file, response_id: int) -> str:
    """Сохраняет изображение ответа и возвращает путь к нему."""
    media_dir = os.path.join(settings.MEDIA_ROOT, settings.RESPONSES_MEDIA_DIR)
    os.makedirs(media_dir, exist_ok=True)
    
    filename = f"response_{response_id}_{file.filename}"
    file_path = os.path.join(media_dir, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return f"{settings.RESPONSES_MEDIA_DIR}/{filename}"