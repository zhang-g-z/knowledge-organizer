# app/tasks.py

from .celery_app import celery_app

@celery_app.task
def background_task(data):
    # Process data
    pass
