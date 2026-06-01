from pydantic import BaseModel, field_validator
from typing import Optional
import os


class RoomCreate(BaseModel):
    name: str
    max_members: Optional[int] = None

    @field_validator("name")
    @classmethod
    def name_min_length(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Room name must be at least 3 characters")
        return v.strip()

    @field_validator("max_members")
    @classmethod
    def validate_max_members(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 2:
            raise ValueError("max_members must be at least 2")
        return v


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    max_members: Optional[int] = None
    is_active: Optional[bool] = None


class RoomResponse(BaseModel):
    id: int
    name: str
    creator_id: int
    max_members: int
    is_active: bool
    member_count: Optional[int] = None

    model_config = {"from_attributes": True}
