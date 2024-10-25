from celery import Celery
from app.core.config import settings

# Initialize the Celery application
celery_app = Celery(
    settings.PROJECT_NAME,
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Load custom configurations if needed
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    broker_connection_retry_on_startup=True,
    enable_utc=True
)

# Optional: you can define periodic tasks here
# from celery.schedules import crontab
# celery_app.conf.beat_schedule = {
#     "sample_task": {
#         "task": "app.workers.tasks.sample_task",
#         "schedule": crontab(minute=0, hour=0),  # Runs every day at midnight
#     },
# }

# Discover tasks from tasks.py (auto-discover if in a package)
# celery_app.autodiscover_tasks(["app.tasks.ai_tasks"])
