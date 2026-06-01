from sqlalchemy import BigInteger, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    memberships: Mapped[list["RoomMember"]] = relationship("RoomMember", back_populates="user", cascade="all, delete-orphan")
    sent_messages: Mapped[list["Message"]] = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    created_rooms: Mapped[list["Room"]] = relationship("Room", back_populates="creator")

    def __eq__(self, other): return isinstance(other, User) and self.id == other.id
    def __hash__(self): return hash(self.id)
    def __str__(self): return f"User({self.username})"
    def __repr__(self): return f"<User id={self.id} username={self.username} role={self.role}>"
