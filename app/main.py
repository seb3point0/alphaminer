import logging
from fastapi import FastAPI
from app.workers.tasks import sample_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
project_name = "alphaminer"

@app.on_event("startup")
def startup_event():
    logger.info(f"Startup: {project_name}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": f"Welcome {project_name}!"}

@app.post("/add/{x}/{y}")
def add(x: int, y: int):
    task = sample_task.delay(x, y)
    return {"task_id": task.id, "status": "Task submitted!"}
