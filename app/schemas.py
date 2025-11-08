from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PydanticBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TagBase(PydanticBase):
    name: str

class Tag(TagBase):
    id: int


class KnowledgeCreate(PydanticBase):
    text: str  # 原始输入文本

class KnowledgeUpdate(PydanticBase):
    title: Optional[str]
    description: Optional[str]
    summary: Optional[str]
    tags: Optional[List[str]]

class KnowledgeListItem(PydanticBase):
    id: int
    title: Optional[str]
    description: Optional[str]
    summary: Optional[str]
    tags: List[Tag]
    status: str
    source: Optional[str]
    created_at: Optional[datetime]

class KnowledgeDetail(KnowledgeListItem):
    original_text: str
    llm_raw: Optional[str]
    confidence: Optional[str]