from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.repositories.message_repository import MessageRepository
from app.repositories.receipt_repository import ReceiptRepository
from app.models.message import Message
from app.utils.exceptions import NotFoundError, ForbiddenError, MessageDeletedError
from app.schemas.search import MessageSearchRequest, MessageSearchResponse, MessageSearchResult

DEFAULT_PAGE_SIZE = 20


class MessageService:
    def __init__(self, db: AsyncSession):
        self.repo = MessageRepository(db)

    def _format(self, msg: Message, delivered_to: list[int] = None, read_by: list[int] = None) -> dict:
        return {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "room_id": msg.room_id,
            "recipient_id": msg.recipient_id,
            "content": "[deleted]" if msg.is_deleted else msg.content,
            "is_deleted": msg.is_deleted,
            "created_at": msg.created_at,
            "delivered_to": delivered_to or [],
            "read_by": read_by or [],
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
        receipt_repo = ReceiptRepository(self.repo.db)
        result = []
        for m in messages:
            delivered_to = await receipt_repo.get_delivered_user_ids(m.id)
            read_by = await receipt_repo.get_read_user_ids(m.id)
            result.append(self._format(m, delivered_to, read_by))
        return {"messages": result, "next_cursor": next_cursor}

    async def get_private_history(
        self, user_id: int, other_user_id: int, limit: int = DEFAULT_PAGE_SIZE, cursor: Optional[int] = None
    ) -> dict:
        messages = await self.repo.get_private_messages(user_id, other_user_id, limit + 1, cursor)
        has_more = len(messages) > limit
        messages = messages[:limit]
        next_cursor = messages[-1].id if has_more and messages else None
        receipt_repo = ReceiptRepository(self.repo.db)
        result = []
        for m in messages:
            delivered_to = await receipt_repo.get_delivered_user_ids(m.id)
            read_by = await receipt_repo.get_read_user_ids(m.id)
            result.append(self._format(m, delivered_to, read_by))
        return {"messages": result, "next_cursor": next_cursor}

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

    async def search(self, req: MessageSearchRequest) -> MessageSearchResponse:
        rows = await self.repo.search(
            req.room_id, req.keyword, req.sender_id,
            req.from_date, req.to_date, req.limit + 1, req.cursor
        )
        has_more = len(rows) > req.limit
        rows = rows[:req.limit]
        next_cursor = rows[-1][0].id if has_more and rows else None
        messages = [
            MessageSearchResult(
                id=msg.id,
                sender_id=msg.sender_id,
                username=username,
                room_id=msg.room_id,
                room_name=room_name,
                content=msg.content,
                created_at=msg.created_at,
            )
            for msg, username, room_name in rows
        ]
        return MessageSearchResponse(messages=messages, next_cursor=next_cursor)

    async def get_missed_messages(self, room_id: int, after_message_id: int) -> list[dict]:
        messages = await self.repo.get_missed_messages(room_id, after_message_id)
        receipt_repo = ReceiptRepository(self.repo.db)
        result = []
        for m in messages:
            delivered_to = await receipt_repo.get_delivered_user_ids(m.id)
            read_by = await receipt_repo.get_read_user_ids(m.id)
            result.append(self._format(m, delivered_to, read_by))
        return result
