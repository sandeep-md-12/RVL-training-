from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# from sqlalchemy.sql import func
from typing import Optional
from app.models.message_receipt import MessageReceipt
from datetime import datetime, timezone


class ReceiptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, message_id: int, user_id: int) -> Optional[MessageReceipt]:
        result = await self.db.execute(
            select(MessageReceipt).where(
                MessageReceipt.message_id == message_id,
                MessageReceipt.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_message(self, message_id: int) -> list[MessageReceipt]:
        result = await self.db.execute(
            select(MessageReceipt).where(MessageReceipt.message_id == message_id)
        )
        return list(result.scalars().all())

    async def mark_delivered(self, message_id: int, user_id: int) -> MessageReceipt:
        receipt = await self.get(message_id, user_id)
        if not receipt:
            receipt = MessageReceipt(message_id=message_id, user_id=user_id)
            self.db.add(receipt)
        if not receipt.is_delivered:
            receipt.is_delivered = True
            receipt.delivered_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(receipt)
        return receipt

    async def mark_read(self, message_id: int, user_id: int) -> MessageReceipt:
        receipt = await self.get(message_id, user_id)
        if not receipt:
            receipt = MessageReceipt(
                message_id=message_id, user_id=user_id,
                is_delivered=True, delivered_at=datetime.now(timezone.utc)
            )
            self.db.add(receipt)
        if not receipt.is_read:
            receipt.is_read = True
            receipt.read_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(receipt)
        return receipt

    async def get_delivered_user_ids(self, message_id: int) -> list[int]:
        result = await self.db.execute(
            select(MessageReceipt.user_id).where(
                MessageReceipt.message_id == message_id,
                MessageReceipt.is_delivered == True,
            )
        )
        return list(result.scalars().all())

    async def get_read_user_ids(self, message_id: int) -> list[int]:
        result = await self.db.execute(
            select(MessageReceipt.user_id).where(
                MessageReceipt.message_id == message_id,
                MessageReceipt.is_read == True,
            )
        )
        return list(result.scalars().all())
