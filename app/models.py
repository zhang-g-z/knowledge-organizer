from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

# Many-to-many
knowledge_tag_table = Table(
    "knowledge_tag",
    Base.metadata,
    Column("knowledge_id", Integer, ForeignKey("knowledge_items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), index=True, nullable=True)
    description = Column(String(1024), nullable=True)
    summary = Column(Text, nullable=True)
    original_text = Column(Text, nullable=False)
    llm_raw = Column(Text, nullable=True)         # 原始 LLM 输出（JSON 或文本）
    confidence = Column(String(64), nullable=True)  # 置信度或评分（可为空）
    source = Column(String(32), nullable=True, default="local")  # 'llm' 或 'local'
    status = Column(String(32), nullable=False, default="pending")  # pending/processing/done/failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tags = relationship("Tag", secondary=knowledge_tag_table, back_populates="items")
    owner = relationship("User", back_populates="items")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)

    items = relationship("KnowledgeItem", secondary=knowledge_tag_table, back_populates="tags")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(150), nullable=True)
    phone = Column(String(32), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("KnowledgeItem", back_populates="owner")