from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.repositories.message_repository import MessageRepository
from app.models.message import Message
from app.utils.exceptions import NotFoundError, ForbiddenError, MessageDeletedError

DEFAULT_PAGE_SIZE = 20


class MessageService:
    def __init__(self, db: AsyncSession):
        self.repo = MessageRepository(db)

    def _format(self, msg: Message) -> dict:
        return {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "room_id": msg.room_id,
            "recipient_id": msg.recipient_id,
            "content": "[deleted]" if msg.is_deleted else msg.content,
            "is_deleted": msg.is_deleted,
            "created_at": msg.created_at,
        }

    async def save_room_message(self, sender_id: int, room_id: int, content: str) -> dict:
        msg = Message(sender_id=sender_id, room_id=room_id, content=content)
        created = await self.repo.create(msg)
        return self._format(created)

    async def save_private_message(self, sender_id: int, recipient_id: int, content: str) -> dict:
        msg = Message(sender_id=sender_id, recipient_id=recipient_id, content=content)
        created = await self.repo.create(msg)
        return self._format(created)

    async def get_room_history(
        self, room_id: int, limit: int = DEFAULT_PAGE_SIZE, cursor: Optional[int] = None
    ) -> dict:
        messages = await self.repo.get_room_messages(room_id, limit + 1, cursor)
        has_more = len(messages) > limit
        messages = messages[:limit]
        next_cursor = messages[-1].id if has_more and messages else None
        return {"messages": [self._format(m) for m in messages], "next_cursor": next_cursor}

    async def get_private_history(
        self, user_id: int, other_user_id: int, limit: int = DEFAULT_PAGE_SIZE, cursor: Optional[int] = None
    ) -> dict:
        messages = await self.repo.get_private_messages(user_id, other_user_id, limit + 1, cursor)
        has_more = len(messages) > limit
        messages = messages[:limit]
        next_cursor = messages[-1].id if has_more and messages else None
        return {"messages": [self._format(m) for m in messages], "next_cursor": next_cursor}

    async def soft_delete(self, message_id: int, requester_id: int, requester_role: str) -> dict:
        msg = await self.repo.get_by_id(message_id)
        if not msg:
            raise NotFoundError("Message", message_id)
        if msg.is_deleted:
            raise MessageDeletedError()
        if requester_role != "admin" and msg.sender_id != requester_id:
            raise ForbiddenError("You can only delete your own messages")
        msg.is_deleted = True
        updated = await self.repo.update(msg)
        return self._format(updated)
