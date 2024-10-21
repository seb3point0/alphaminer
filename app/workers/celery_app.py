from celery import Celery
import os

# Load environment variables from the .env file or default values
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize the Celery application
celery_app = Celery(
    "my_fastapi_app",               # Name of the app
    broker=REDIS_URL,               # Message broker (Redis in this case)
    backend=REDIS_URL               # Backend where results are stored (Redis here too)
)

# Load custom configurations if needed
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],        # Ensure tasks are serialized with JSON
    result_serializer="json",
    timezone="UTC",                 # Set your timezone
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
celery_app.autodiscover_tasks(["app.workers.tasks"])