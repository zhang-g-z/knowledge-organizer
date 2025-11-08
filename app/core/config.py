from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 异步 MySQL URL（asyncmy）
    DATABASE_URL: str = "mysql+aiomysql://root:qwe#113.@127.0.0.1:3306/knowledge_db?charset=utf8mb4"
    FRONTEND_DIST_DIR: str = "frontend_dist"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT: int = 30

    # Celery / Redis
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    REDIS_PUBSUB_CHANNEL: str = "knowledge_updates"
    # JWT / Auth
    SECRET_KEY: str = "change-me-to-a-secure-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()