from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.utils.database import get_db
from app.controllers.room_controller import RoomController
from app.schemas.room import RoomCreate, RoomResponse
from app.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post("/", response_model=RoomResponse, status_code=201)
async def create_room(
    data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await RoomController(db).create_room(data.name, current_user.id, data.max_members)


@router.get("/", response_model=List[RoomResponse])
async def get_rooms(
    joined: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await RoomController(db).get_all_rooms(current_user.id, joined)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await RoomController(db).get_room(room_id)


@router.post("/{room_id}/join", response_model=RoomResponse)
async def join_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await RoomController(db).join_room(room_id, current_user.id)


@router.post("/{room_id}/leave", status_code=204)
async def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await RoomController(db).leave_room(room_id, current_user.id)


@router.delete("/{room_id}/members/{user_id}", status_code=204)
async def kick_member(
    room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await RoomController(db).kick_member(room_id, user_id, current_user.id, current_user.role.value)


@router.delete("/{room_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await RoomController(db).delete_room(room_id, current_user.id, current_user.role.value)
