import random
from typing import List, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
from app.models.models import Task
from app.schemas.schemas import TaskCreate
from app.core.config import settings
from enum import Enum

class TaskCategory(Enum):
    CREATIVE = "creative"
    PHOTO = "photo"
    WRITING = "writing"
    MUSIC = "music"
    DRAWING = "drawing"
    ACTING = "acting"

# Расширенный список заданий с категориями
TASKS_BY_CATEGORY = {
    TaskCategory.CREATIVE: [
        "Напиши письмо своему холодильнику.",
        "Создай скульптуру из бумаги и скотча.",
        "Создай новый бренд одежды для животных.",
        "Создай новый язык жестов для общения с растениями.",
    ],
    TaskCategory.PHOTO: [
        "Сфотографируй свою тень в стиле нуар.",
        "Сфотографируй 5 случайных предметов в доме и придумай историю о том, как они связаны.",
        "Сфотографируй себя в 5 разных стилях.",
    ],
    TaskCategory.WRITING: [
        "Напиши короткий рассказ, где главный герой - твоя любимая еда.",
        "Напиши письмо своему 'я' из прошлого.",
        "Напиши короткий диалог между двумя предметами в твоей комнате.",
    ],
    TaskCategory.MUSIC: [
        "Составь плейлист из 5 песен, описывающих твой день.",
    ],
    TaskCategory.DRAWING: [
        "Нарисуй портрет своего питомца в стиле известного художника.",
        "Сделай коллаж из случайных изображений из интернета.",
    ],
    TaskCategory.ACTING: [
        "Сообщи всем вокруг важную новость... на языке жестов.",
        "Сделай анимацию из 10 кадров в стиле гифки, показывающую твой утренний ритуал.",
    ]
}

def generate_random_task(category: Optional[TaskCategory] = None) -> str:
    """Генерирует случайное задание из предопределенного списка."""
    if category and category in TASKS_BY_CATEGORY:
        return random.choice(TASKS_BY_CATEGORY[category])
    else:
        all_tasks = [task for tasks in TASKS_BY_CATEGORY.values() for task in tasks]
        return random.choice(all_tasks)

def generate_task_with_ai(prompt: Optional[str] = None) -> str:
    """Генерирует задание с помощью AI."""
    if not settings.OPENAI_API_KEY:
        # Если нет API ключа, возвращаем случайное задание
        return generate_random_task()
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    base_prompt = "Сгенерируй творческое задание для пользователя. Задание должно быть необычным, веселым и вдохновляющим. Ответ должен содержать только само задание, без дополнительных пояснений."
    
    if prompt:
        full_prompt = f"{base_prompt} Тема: {prompt}"
    else:
        full_prompt = base_prompt
    
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Ты помощник, который генерирует творческие задания."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=100,
            temperature=0.8
        )
        
        task_text = response.choices[0].message.content.strip()
        return task_text
    except Exception as e:
        # В случае ошибки возвращаем случайное задание
        print(f"Error generating task with AI: {e}")
        return generate_random_task()

def create_task(db: Session, task: TaskCreate, creator_id: Optional[int] = None) -> Task:
    """Создает новое задание в базе данных."""
    db_task = Task(**task.model_dump(), creator_id=creator_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Получает задание по ID."""
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """Получает список заданий."""
    return db.query(Task).offset(skip).limit(limit).all()