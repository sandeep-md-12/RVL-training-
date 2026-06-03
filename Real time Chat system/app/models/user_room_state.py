from sqlalchemy import BigInteger, Integer, ForeignKey,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.database import Base
from typing import Optional


class UserRoomState(Base):
    __tablename__ = "user_room_states"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rooms.id"), nullable=False)
    unread_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_read_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("messages.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


    user: Mapped["User"] = relationship("User")
    room: Mapped["Room"] = relationship("Room")
