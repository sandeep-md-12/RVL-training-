from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.user_room_state import UserRoomState


class UserRoomStateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int, room_id: int) -> Optional[UserRoomState]:
        result = await self.db.execute(
            select(UserRoomState).where(
                UserRoomState.user_id == user_id,
                UserRoomState.room_id == room_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: int, room_id: int) -> UserRoomState:
        state = await self.get(user_id, room_id)
        if not state:
            state = UserRoomState(user_id=user_id, room_id=room_id)
            self.db.add(state)
            await self.db.commit()
            await self.db.refresh(state)
        return state

    async def increment_unread(self, user_id: int, room_id: int):
        state = await self.get_or_create(user_id, room_id)
        state.unread_count += 1
        await self.db.commit()
    
    async def reset_unread(self, user_id: int, room_id: int, last_message_id: int):
        state = await self.get_or_create(user_id, room_id)
        state.unread_count = 0
        state.last_read_message_id = last_message_id
        await self.db.commit()
        await self.db.refresh(state)
        return state

    async def get_last_read_message_id(self, user_id: int, room_id: int) -> Optional[int]:
        state = await self.get(user_id, room_id)
        return state.last_read_message_id if state else None
