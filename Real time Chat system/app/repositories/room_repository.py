from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.models.room import Room
from app.models.room_member import RoomMember


class RoomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, room: Room) -> Room:
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def get_by_id(self, room_id: int) -> Optional[Room]:
        result = await self.db.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Room]:
        result = await self.db.execute(select(Room).where(Room.name == name))
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Room]:
        result = await self.db.execute(select(Room).where(Room.is_active == True))
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> list[Room]:
        result = await self.db.execute(
            select(Room)
            .join(RoomMember, RoomMember.room_id == Room.id)
            .where(RoomMember.user_id == user_id, Room.is_active == True)
        )
        return list(result.scalars().all())

    async def update(self, room: Room) -> Room:
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def delete(self, room: Room):
        await self.db.delete(room)
        await self.db.commit()

    async def member_count(self, room_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).where(RoomMember.room_id == room_id)
        )
        return result.scalar_one()
