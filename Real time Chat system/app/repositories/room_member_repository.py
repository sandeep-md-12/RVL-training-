from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.room_member import RoomMember


class RoomMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, member: RoomMember) -> RoomMember:
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def get(self, room_id: int, user_id: int) -> Optional[RoomMember]:
        result = await self.db.execute(
            select(RoomMember).where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_room(self, room_id: int) -> list[RoomMember]:
        result = await self.db.execute(
            select(RoomMember).where(RoomMember.room_id == room_id)
        )
        return list(result.scalars().all())

    async def delete(self, member: RoomMember):
        await self.db.delete(member)
        await self.db.commit()
