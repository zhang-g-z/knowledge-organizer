from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .core.config import settings

# 使用 SQLAlchemy async engine
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# FastAPI 依赖
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session