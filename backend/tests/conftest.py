import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

os.environ['POSTGRES_USER'] = 'test_user'
os.environ['POSTGRES_PASSWORD'] = 'test_password'
os.environ['POSTGRES_DB'] = 'test_db'
os.environ['DATABASE_URL'] = "sqlite:///./test.db"
os.environ['REDIS_URL'] = "redis://localhost:6379/0"
os.environ['SECRET_KEY'] = "test-secret-key-for-tests"


from app.core.config import settings
SQLALCHEMY_DATABASE_URL = settings.database_url # Это будет "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
