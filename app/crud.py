from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from . import models, schemas

async def get_or_create_tag(db: AsyncSession, tag_name: str):
    q = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
    tag = q.scalars().first()
    if not tag:
        tag = models.Tag(name=tag_name)
        db.add(tag)
        await db.flush()
    return tag


async def get_user_by_username(db: AsyncSession, username: str):
    q = await db.execute(select(models.User).filter(models.User.username == username))
    return q.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    q = await db.execute(select(models.User).filter(models.User.email == email))
    return q.scalars().first()


async def get_user_by_phone(db: AsyncSession, phone: str):
    q = await db.execute(select(models.User).filter(models.User.phone == phone))
    return q.scalars().first()


async def create_user(db: AsyncSession, username: str, hashed_password: str, name: str | None = None, phone: str | None = None, email: str | None = None):
    user = models.User(username=username, hashed_password=hashed_password, name=name, phone=phone, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user



async def create_knowledge(db: AsyncSession, text: str, user_id: int):
    item = models.KnowledgeItem(
        title=None,
        description=None,
        summary=None,
        original_text=text,
        status="pending",
        source="local"
    )
    item.user_id = user_id
    db.add(item)
    await db.commit()
    await db.refresh(item)
    # 返回刚创建的 id（避免在这里直接返回 ORM 对象导致后续懒加载）
    return item

async def list_knowledge(db: AsyncSession, skip: int = 0, limit: int = 10, q: str | None = None, user_id: Optional[int] = None) -> List[models.KnowledgeItem]:
    """List knowledge items with optional search across title, description, summary and tag names.

    Args:
        db: AsyncSession
        skip: offset
        limit: page size
        q: optional search string

    Returns:
        list of KnowledgeItem
    """
    stmt = select(models.KnowledgeItem).options(selectinload(models.KnowledgeItem.tags))

    # always scope to the given user if provided
    if user_id is not None:
        stmt = stmt.filter(models.KnowledgeItem.user_id == user_id)

    if q:
        pattern = f"%{q}%"
        # join to tags to allow searching by tag name; use outerjoin so items without tags are still considered
        stmt = (
            stmt
            .outerjoin(models.KnowledgeItem.tags)
            .where(
                or_(
                    models.KnowledgeItem.title.ilike(pattern),
                    models.KnowledgeItem.description.ilike(pattern),
                    models.KnowledgeItem.summary.ilike(pattern),
                    models.Tag.name.ilike(pattern),
                )
            )
            .distinct()
        )

    stmt = stmt.order_by(models.KnowledgeItem.created_at.desc()).offset(skip).limit(limit)

    res = await db.execute(stmt)
    return res.scalars().unique().all()

async def get_knowledge(db: AsyncSession, item_id: int, user_id: Optional[int] = None) -> Optional[models.KnowledgeItem]:
    stmt = select(models.KnowledgeItem).options(selectinload(models.KnowledgeItem.tags)).filter(models.KnowledgeItem.id == item_id)
    if user_id is not None:
        stmt = stmt.filter(models.KnowledgeItem.user_id == user_id)
    q = await db.execute(stmt)
    return q.scalars().first()

async def delete_knowledge(db: AsyncSession, item_id: int, user_id: Optional[int] = None) -> bool:
    item = await get_knowledge(db, item_id, user_id=user_id)
    if item:
        await db.delete(item)
        await db.commit()
        return True
    return False

async def update_after_extraction(db: AsyncSession, item_id: int, extracted: dict):
    item = await get_knowledge(db, item_id)
    if not item:
        return None
    # update fields
    item.title = extracted.get("title") or item.title
    item.description = extracted.get("description") or item.description
    item.summary = extracted.get("summary") or item.summary
    item.llm_raw = extracted.get("llm_raw")
    item.confidence = extracted.get("confidence")
    item.source = extracted.get("source", "llm")
    item.status = extracted.get("status", "done")

    # tags: reset
    tags = extracted.get("tags", [])
    item.tags = []
    for t in tags:
        tag_obj = await get_or_create_tag(db, t)
        item.tags.append(tag_obj)

    await db.commit()
    await db.refresh(item)
    return item

async def mark_processing(db: AsyncSession, item_id: int):
    item = await get_knowledge(db, item_id)
    if not item:
        return None
    item.status = "processing"
    await db.commit()
    await db.refresh(item)
    return item

async def mark_failed(db: AsyncSession, item_id: int, reason: str = ""):
    item = await get_knowledge(db, item_id)
    if not item:
        return None
    item.status = "failed"
    item.llm_raw = (item.llm_raw or "") + f"\n\nFAILED_REASON: {reason}"
    await db.commit()
    await db.refresh(item)
    return item