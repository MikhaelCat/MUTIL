from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.models.models import Task, Response
from sqlalchemy import or_

router = APIRouter()

@router.get("/tasks")
def search_tasks(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Поиск заданий по тексту."""
    tasks = db.query(Task).filter(
        or_(
            Task.text.contains(query),
            Task.tags.any(name=query) 
        )
    ).all()
    return tasks

@router.get("/responses")
def search_responses(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Поиск ответов по тексту."""
    responses = db.query(Response).filter(
        Response.text.contains(query)
    ).all()
    return responses