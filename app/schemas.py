from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Any

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


class UserCreate(PydanticBase):
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6)
    # optional display name
    name: Optional[str] = Field(None, max_length=150)
    # require phone and email for registration
    phone: str = Field(..., min_length=7, max_length=32)
    email: EmailStr


class UserRead(PydanticBase):
    id: int
    username: str
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    created_at: Optional[datetime]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class PasswordChange(PydanticBase):
    old_password: str
    new_password: str
    confirm_password: str