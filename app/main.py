import logging
from fastapi import FastAPI
from app.core.config import settings
from app.workers.tasks import sample_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

@app.on_event("startup")
def startup_event():
    logger.info(f"Startup: {settings.PROJECT_NAME}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": f"Welcome {settings.PROJECT_NAME}!"}

@app.get("/task/{x}")
def add(x: int):
    task = sample_task.delay(x)
    return {"task_id": task.id, "status": "Task submitted!"}
