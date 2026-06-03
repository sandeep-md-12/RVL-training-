from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.controllers.user_controller import UserController
from app.schemas.user import UserResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.room_member_repository import RoomMemberRepository
from app.repositories.user_repository import UserRepository
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/online", response_model=List[UserResponse])
async def get_online_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await UserController(db).get_online()


@router.get("/online/room/{room_id}", response_model=List[UserResponse])
async def get_online_users_in_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    members = await RoomMemberRepository(db).get_by_room(room_id)
    user_repo = UserRepository(db)
    result = []
    for m in members:
        u = await user_repo.get_by_id(m.user_id)
        if u and u.is_online:
            result.append(u)
    return result


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await UserController(db).get_all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await UserController(db).get_by_id(user_id)
