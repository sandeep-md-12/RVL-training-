from sqlalchemy import BigInteger, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    max_members: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    creator: Mapped["User"] = relationship("User", back_populates="created_rooms")
    members: Mapped[list["RoomMember"]] = relationship("RoomMember", back_populates="room", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="room", cascade="all, delete-orphan")

    def __eq__(self, other): return isinstance(other, Room) and self.id == other.id
    def __hash__(self): return hash(self.id)
    def __str__(self): return f"Room({self.name})"
    def __repr__(self): return f"<Room id={self.id} name={self.name} active={self.is_active}>"
