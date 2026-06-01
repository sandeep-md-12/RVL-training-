from sqlalchemy import BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.utils.database import Base
from datetime import datetime


class RoomMember(Base):
    __tablename__ = "room_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rooms.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    def __eq__(self, other): return isinstance(other, RoomMember) and self.id == other.id
    def __hash__(self): return hash(self.id)
    def __str__(self): return f"RoomMember(room={self.room_id}, user={self.user_id})"
    def __repr__(self): return f"<RoomMember room_id={self.room_id} user_id={self.user_id}>"
