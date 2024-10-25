from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/")
def read_root():
    return {"message": f"Welcome {settings.PROJECT_NAME}!"}