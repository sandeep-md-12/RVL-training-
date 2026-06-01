from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional
from app.services.message_service import MessageService
from app.schemas.message import MessageCreate
from app.utils.exceptions import NotFoundError, ForbiddenError, MessageDeletedError


class MessageController:
    def __init__(self, db: AsyncSession):
        self.service = MessageService(db)

    async def save_room_message(self, sender_id: int, room_id: int, content: str) -> dict:
        return await self.service.save_room_message(sender_id, room_id, content)

    async def save_private_message(self, sender_id: int, recipient_id: int, content: str) -> dict:
        return await self.service.save_private_message(sender_id, recipient_id, content)

    async def send_room_message(self, sender_id: int, body: MessageCreate) -> dict:
        if not body.room_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="room_id is required")
        return await self.service.save_room_message(sender_id, body.room_id, body.content)

    async def send_private_message(self, sender_id: int, body: MessageCreate) -> dict:
        if not body.recipient_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="recipient_id is required")
        return await self.service.save_private_message(sender_id, body.recipient_id, body.content)

    async def get_room_history(self, room_id: int, limit: int = 20, cursor: Optional[int] = None) -> dict:
        return await self.service.get_room_history(room_id, limit, cursor)

    async def get_private_history(self, user_id: int, other_user_id: int, limit: int = 20, cursor: Optional[int] = None) -> dict:
        return await self.service.get_private_history(user_id, other_user_id, limit, cursor)

    async def soft_delete(self, message_id: int, requester_id: int, requester_role: str) -> dict:
        try:
            return await self.service.soft_delete(message_id, requester_id, requester_role)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except MessageDeletedError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
