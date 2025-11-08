# https://github.com/zhang-g-z/knowledge-organizer/blob/master/app/tasks.py
import asyncio
import json
from celery.utils.log import get_task_logger
from app.celery_task.celery import celery
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app import models
from app.utils.extractor_async import extract_from_text_async
import redis  # 同步 redis 用于在 Celery worker（同步）中发布通知

logger = get_task_logger(__name__)

# Celery worker: async engine for DB updates
async_engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# 使用同步 redis client (worker process is sync) 来 publish 通知
redis_client = redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

@celery.task(bind=True)
def extract_and_update(self, item_id: int):
    try:
        asyncio.run(_run_extraction_and_update(item_id))
        return {"ok": True}
    except Exception as e:
        logger.exception("Task failed: %s", e)
        return {"ok": False, "error": str(e)}

async def _run_extraction_and_update(item_id: int):
    async with AsyncSessionLocal() as db:
        q = await db.execute(__import__('sqlalchemy').select(models.KnowledgeItem).filter(models.KnowledgeItem.id == item_id))
        item = q.scalars().first()
        if not item:
            logger.error("Item %s not found", item_id)
            return
        item.status = "processing"
        print(item)
        await db.commit()
        await db.refresh(item)
        try:
            extracted = await extract_from_text_async(item.original_text)
            from app.crud import update_after_extraction
            await update_after_extraction(db, item_id, extracted)
            payload = json.dumps({"id": item_id, "status": "done"})
            # 使用同步 redis client 发布消息
            redis_client.publish(settings.REDIS_PUBSUB_CHANNEL, payload)
        except Exception as e:
            logger.exception("Extraction failed for item %s: %s", item_id, e)
            item.status = "failed"
            item.llm_raw = (item.llm_raw or "") + f"\n\nTASK_ERROR: {e}"
            await db.commit()
            payload = json.dumps({"id": item_id, "status": "failed", "error": str(e)})
            redis_client.publish(settings.REDIS_PUBSUB_CHANNEL, payload)