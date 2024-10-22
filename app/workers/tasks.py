from app.celery import celery_app
import time

# Example task that simulates some processing work
@celery_app.task
def sample_task(data: dict):
    print(f"Processing data: {data}")
    time.sleep(5)  # Simulate a delay in the background
    return {"status": "completed", "processed_data": data}