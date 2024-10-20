import os
from celery import Celery

broker_url = "redis://redis:6379/0"

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=broker_url,
    task_serializer = 'json',
    result_serializer = 'json',
    accept_content = ['json'],
    timezone = 'UTC',
    enable_utc = True
)

@celery_app.task
def example_task(x, y):
    return x + y