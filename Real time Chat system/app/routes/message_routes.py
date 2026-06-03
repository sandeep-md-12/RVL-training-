from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.utils.database import get_db
from app.controllers.message_controller import MessageController
from app.schemas.message import MessageCreate, MessageHistoryResponse, MessageResponse
from app.schemas.search import MessageSearchRequest, MessageSearchResponse
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/room", response_model=MessageResponse)
async def send_room_message(
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageController(db).send_room_message(current_user.id, body)


@router.post("/private", response_model=MessageResponse)
async def send_private_message(
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageController(db).send_private_message(current_user.id, body)


@router.get("/rooms/{room_id}", response_model=MessageHistoryResponse)
async def get_room_messages(
    room_id: int,
    limit: int = 20,
    cursor: Optional[int] = None,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageController(db).get_room_history(room_id, limit, cursor)


@router.get("/private/{other_user_id}", response_model=MessageHistoryResponse)
async def get_private_messages(
    other_user_id: int,
    limit: int = 20,
    cursor: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageController(db).get_private_history(current_user.id, other_user_id, limit, cursor)


@router.delete("/{message_id}", response_model=MessageResponse)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageController(db).soft_delete(message_id, current_user.id, current_user.role.value)


@router.post("/search", response_model=MessageSearchResponse)
async def search_messages(
    body: MessageSearchRequest,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageController(db).search(body)
