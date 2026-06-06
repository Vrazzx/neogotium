# backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/aipm"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Опциональные — beat не нуждается в них
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""

    CF_PROXY_URL: str = ""
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = False
    WHISPER_MODEL: str = "base"

    YANDEX_OAUTH_TOKEN: str = ""
    YOUGILE_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"   # игнорировать неизвестные переменные

settings = Settings()