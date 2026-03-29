from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: Optional[str] = "新对话"


class SessionUpdate(BaseModel):
    title: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionDetailOut(SessionOut):
    messages: list[MessageOut]
