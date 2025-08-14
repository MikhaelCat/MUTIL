from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Dependency для получения сессии БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()