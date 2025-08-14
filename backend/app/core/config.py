import redis
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "MUTIL"
    DEBUG: bool = False
    SECRET_KEY: str = "your-super-secret-key-change-in-production"

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_HOST: str = "db"
    DATABASE_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_URL: str

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # Media files
    MEDIA_ROOT: str = "/app/media"
    RESPONSES_MEDIA_DIR: str = "responses"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"


settings = Settings()

# Инициализация Redis клиента
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)