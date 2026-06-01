from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    content: str
    room_id: Optional[int] = None
    recipient_id: Optional[int] = None


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_deleted: Optional[bool] = None


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    room_id: Optional[int]
    recipient_id: Optional[int]
    content: str
    is_deleted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageHistoryResponse(BaseModel):
    messages: list[MessageResponse]
    next_cursor: Optional[int]
