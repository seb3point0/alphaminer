from app.workers.celery_app import celery_app

# Import your Celery instance and ensure it starts when running this script
if __name__ == "__main__":
    celery_app.start()