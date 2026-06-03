from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageSearchRequest(BaseModel):
    keyword: str
    room_id: int
    sender_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = 20
    cursor: Optional[int] = None


class MessageSearchResult(BaseModel):
    id: int
    sender_id: int
    username: str
    room_id: int
    room_name: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageSearchResponse(BaseModel):
    messages: list[MessageSearchResult]
    next_cursor: Optional[int]
