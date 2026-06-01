from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.controllers.user_controller import UserController
from app.schemas.user import UserResponse
from app.dependencies import get_current_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/online", response_model=List[UserResponse])
async def get_online_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await UserController(db).get_online()


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
