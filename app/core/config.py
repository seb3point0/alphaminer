from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    DEBUG: bool = os.getenv("DEBUG")
    
    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL")
    
    # Additional fields from your .env file
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
    FLOWER_PORT: int = int(os.getenv("FLOWER_PORT"))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    PGADMIN_PORT: int = int(os.getenv("PGADMIN_PORT"))
    WEB_PORT: int = int(os.getenv("WEB_PORT"))

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
