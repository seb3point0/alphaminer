import logging
import asyncio
from fastapi import FastAPI
from app.core.config import settings
from app.services.telegram import setup_bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_name = settings.PROJECT_NAME

app = FastAPI(title=project_name, debug=settings.DEBUG)

@app.on_event("startup")
def startup_event():
    logger.info(f"Startup: {project_name}")
    asyncio.create_task(setup_bot(settings.TELEGRAM_TOKEN))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": f"Welcome {project_name}!"}

# @app.get("/task/{x}")
# def add(x: int):
#     task = sample_task.delay(x)
#     return {"task_id": task.id, "status": "Task submitted!"}
