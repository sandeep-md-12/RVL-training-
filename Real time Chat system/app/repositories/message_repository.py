from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from typing import Optional
from datetime import datetime
from app.models.message import Message
from app.models.user import User
from app.models.room import Room


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_by_id(self, message_id: int) -> Optional[Message]:
        result = await self.db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    async def get_room_messages(
        self, room_id: int, limit: int, cursor: Optional[int]
    ) -> list[Message]:
        query = select(Message).where(Message.room_id == room_id)
        if cursor:
            query = query.where(Message.id < cursor)
        query = query.order_by(Message.id.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_private_messages(
        self, user_id: int, other_user_id: int, limit: int, cursor: Optional[int]
    ) -> list[Message]:
        query = select(Message).where(
            Message.room_id.is_(None),
            or_(
                and_(Message.sender_id == user_id, Message.recipient_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.recipient_id == user_id),
            )
        )
        if cursor:
            query = query.where(Message.id < cursor)
        query = query.order_by(Message.id.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, message: Message) -> Message:
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_missed_messages(self, room_id: int, after_message_id: int) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.room_id == room_id, Message.id > after_message_id)
            .order_by(Message.id.asc())
        )
        return list(result.scalars().all())

    async def search(self, room_id: int, keyword: str, sender_id: Optional[int],
                     from_date: Optional[datetime], to_date: Optional[datetime],
                     limit: int, cursor: Optional[int]) -> list[tuple]:
        query = (
            select(Message, User.username, Room.name)
            .join(User, User.id == Message.sender_id)
            .join(Room, Room.id == Message.room_id)
            .where(
                Message.room_id == room_id,
                Message.is_deleted == False,
                Message.content.ilike(f"%{keyword}%"),
            )
        )
        if sender_id:
            query = query.where(Message.sender_id == sender_id)
        if from_date:
            query = query.where(Message.created_at >= from_date)
        if to_date:
            query = query.where(Message.created_at <= to_date)
        if cursor:
            query = query.where(Message.id < cursor)
        query = query.order_by(Message.id.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.all()
