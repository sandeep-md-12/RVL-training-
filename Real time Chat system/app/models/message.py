from sqlalchemy import BigInteger, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.utils.database import Base
from datetime import datetime
from typing import Optional


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    room_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("rooms.id"), nullable=True)
    recipient_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    room: Mapped[Optional["Room"]] = relationship("Room", back_populates="messages")
    recipient: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recipient_id])

    def __eq__(self, other): return isinstance(other, Message) and self.id == other.id
    def __hash__(self): return hash(self.id)
    def __str__(self): return f"Message(id={self.id}, sender={self.sender_id})"
    def __repr__(self): return f"<Message id={self.id} sender_id={self.sender_id} room_id={self.room_id}>"
