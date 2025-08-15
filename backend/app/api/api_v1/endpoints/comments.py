from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.schemas.schemas import CommentCreate, Comment
from app.models.models import Comment as CommentModel

router = APIRouter()

@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(comment_in: CommentCreate, db: Session = Depends(get_db)):
    """Создает новый комментарий."""
    db_comment = CommentModel(**comment_in.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/response/{response_id}", response_model=List[Comment])
def get_comments_for_response(response_id: int, db: Session = Depends(get_db)):
    """Получает все комментарии для ответа."""
    comments = db.query(CommentModel).filter(CommentModel.response_id == response_id).all()
    return comments