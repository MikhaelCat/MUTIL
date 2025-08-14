from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.schemas.schemas import ResponseCreate, Response, ResponseUpdate
from app.services.response_service import create_response, get_response, get_responses, get_responses_for_task, update_response, delete_response, save_response_image


class ResponseCreateWithFile(BaseModel):
    text: Optional[str] = None
    task_id: int

router = APIRouter()

@router.post("/", response_model=Response, status_code=status.HTTP_201_CREATED)
async def create_new_response(
    task_id: int = Form(...),
    text: Optional[str] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Создает новый ответ с возможной загрузкой изображения."""
    response_in = ResponseCreate(text=text, task_id=task_id)
    db_response = create_response(db, response_in)
    
    if image and image.filename:
        try:
            image_path = save_response_image(image, db_response.id)
            db_response = update_response(db, db_response.id, ResponseUpdate(image_path=image_path))
        except Exception as e:
            delete_response(db, db_response.id)
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    return db_response


@router.post("/", response_model=Response, status_code=status.HTTP_201_CREATED)
def create_new_response(
    response_in: ResponseCreate, 
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Создает новый ответ."""
    db_response = create_response(db, response_in)
    
    if image and image.filename:
        image_path = save_response_image(image, db_response.id)
        db_response = update_response(db, db_response.id, ResponseUpdate(image_path=image_path))
    
    return db_response

@router.get("/{response_id}", response_model=Response)
def read_response(response_id: int, db: Session = Depends(get_db)):
    """Получает ответ по ID."""
    db_response = get_response(db, response_id)
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return db_response

@router.get("/", response_model=List[Response])
def read_responses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получает список ответов."""
    responses = get_responses(db, skip=skip, limit=limit)
    return responses

@router.get("/task/{task_id}", response_model=List[Response])
def read_responses_for_task(task_id: int, db: Session = Depends(get_db)):
    """Получает все ответы для задания."""
    responses = get_responses_for_task(db, task_id)
    return responses

@router.put("/{response_id}", response_model=Response)
def update_existing_response(
    response_id: int, 
    response_in: ResponseUpdate,
    db: Session = Depends(get_db)
):
    """Обновляет ответ."""
    db_response = update_response(db, response_id, response_in)
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return db_response

@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_response(response_id: int, db: Session = Depends(get_db)):
    """Удаляет ответ."""
    success = delete_response(db, response_id)
    if not success:
        raise HTTPException(status_code=404, detail="Response not found")
    return