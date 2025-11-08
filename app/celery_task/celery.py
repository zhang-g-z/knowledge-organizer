from celery import Celery
from app.core.config import settings

# Ensure the tasks module is imported/registered by worker by including it here.
celery = Celery(
    "app.celery_task",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.celery_task.tasks",
    ],
)

# You can configure Celery further here if needed
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)