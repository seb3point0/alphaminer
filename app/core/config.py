from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    DEBUG: bool = os.getenv("DEBUG")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL")
    REDIS_MAX_MEMORY: str = os.getenv("REDIS_MAX_MEMORY")
    REDIS_MAX_MEMORY_POLICY: str = os.getenv("REDIS_MAX_MEMORY_POLICY")
    REDIS_KEY_TTL: int = os.getenv("REDIS_KEY_TTL")
    
    # Telegram
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
