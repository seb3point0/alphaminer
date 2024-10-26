from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    DEBUG: bool = os.getenv("DEBUG")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_MAX_MEMORY: str = os.getenv("REDIS_MAX_MEMORY", "2gb")
    REDIS_MAX_MEMORY_POLICY: str = os.getenv("REDIS_MAX_MEMORY_POLICY", "allkeys-lru")
    
    # Telegram
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
