from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..celery_task.tasks import extract_and_update
from app.core.config import settings

router = APIRouter()

@router.post("/items", response_model=schemas.KnowledgeListItem)
async def create_item(payload: schemas.KnowledgeCreate, db: AsyncSession = Depends(get_db)):
    # 1. 创建记录（pending）
    print(payload.text)
    item = await crud.create_knowledge(db, payload.text)
    # 2. 入队 Celery 后台处理
    extract_and_update.delay(item.id)
    # 3. 重新查询以带上 selectinload 的 tags 和最新字段（避免懒加载）
    item_fresh = await crud.get_knowledge(db, item.id)
    return item_fresh

@router.get("/items", response_model=List[schemas.KnowledgeListItem])
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    q: str | None = Query(None, description="search query to match title, description, summary or tags"),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    items = await crud.list_knowledge(db, skip=skip, limit=page_size, q=q)
    return items

@router.get("/items/count")
async def items_count(db: AsyncSession = Depends(get_db)):
    total = await crud.count_knowledge(db)
    return {"count": total}

@router.get("/items/{item_id}", response_model=schemas.KnowledgeDetail)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_knowledge(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

@router.get("/items/{item_id}/original")
async def get_original(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_knowledge(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": item.id, "original_text": item.original_text}

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_knowledge(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}

@router.put("/items/{item_id}", response_model=schemas.KnowledgeDetail)
async def update_item(item_id: int, payload: schemas.KnowledgeUpdate, db: AsyncSession = Depends(get_db)):
    item = await crud.update_after_extraction(db, item_id, payload.dict(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item