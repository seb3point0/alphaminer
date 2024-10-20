import os
from fastapi import FastAPI
from app.celery_app import example_task

app = FastAPI()
project_name = os.getenv("PROJECT_NAME")

@app.on_event("startup")
def startup_event():
    print(f"Project name: {project_name}")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {project_name}!"}

@app.post("/add/{x}/{y}")
def add(x: int, y: int):
    task = example_task.delay(x, y)
    return {"task_id": task.id, "status": "Task submitted!"}