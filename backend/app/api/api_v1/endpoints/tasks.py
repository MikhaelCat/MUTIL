from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional  
from datetime import timedelta  
from app.api.deps import get_db
from app.schemas.schemas import TaskCreate, Task
from app.services.task_service import generate_random_task, generate_task_with_ai, create_task, get_task, get_tasks

router = APIRouter()

@router.post("/generate", response_model=Task, status_code=status.HTTP_201_CREATED)
def generate_task(
    prompt: Optional[str] = None,
    category: Optional[str] = None,  
    db: Session = Depends(get_db)
):
    """
    Генерирует случайное задание.
    """
    if prompt:
        task_text = generate_task_with_ai(prompt)
    else:
        # task_text = generate_random_task(TaskCategory(category) if category else None)
        task_text = generate_random_task()  
    
    task_in = TaskCreate(text=task_text)
    return create_task(db, task_in)

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_new_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """Создает новое задание."""
    return create_task(db, task_in)

@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Получает задание по ID."""
    db_task = get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.get("/", response_model=List[Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получает список заданий."""
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.post("/generate", response_model=Task, status_code=status.HTTP_201_CREATED)
def generate_task(
    prompt: Optional[str] = None,
    category: Optional[TaskCategory] = None,
    db: Session = Depends(get_db)
):
    """
    Генерирует случайное задание.
    
    ### Параметры:
    - **prompt**: Тема для генерации задания (опционально)
    - **category**: Категория задания (опционально)
    
    ### Ответ:
    - **id**: ID задания
    - **text**: Текст задания
    - **created_at**: Дата создания
    
    ### Примеры:
    ```json
    {
      "text": "Напиши письмо своему холодильнику."
    }
    ```
    """
    if prompt:
        task_text = generate_task_with_ai(prompt)
    else:
        task_text = generate_random_task(category)
    
    task_in = TaskCreate(text=task_text)

    return create_task(db, task_in)

