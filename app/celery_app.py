# app/celery_app.py

from celery import Celery
from app.core.config import Settings

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
)

# Other configurations follow.
