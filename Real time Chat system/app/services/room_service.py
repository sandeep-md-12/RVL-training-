import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.room_repository import RoomRepository
from app.repositories.room_member_repository import RoomMemberRepository
from app.models.room import Room
from app.models.room_member import RoomMember
from app.utils.exceptions import (
    NotFoundError, AlreadyExistsError, RoomFullError,
    AlreadyMemberError, NotMemberError, ForbiddenError
)

DEFAULT_MAX_MEMBERS = int(os.getenv("MAX_ROOM_MEMBERS", 10))


class RoomService:
    def __init__(self, db: AsyncSession):
        self.repo = RoomRepository(db)
        self.member_repo = RoomMemberRepository(db)

    def _format(self, room: Room, member_count: int = None) -> dict:
        return {
            "id": room.id,
            "name": room.name,
            "creator_id": room.creator_id,
            "max_members": room.max_members,
            "is_active": room.is_active,
            "member_count": member_count,
        }

    async def create_room(self, name: str, creator_id: int, max_members: int = None) -> dict:
        if await self.repo.get_by_name(name):
            raise AlreadyExistsError("Room", "name")
        room = Room(
            name=name,
            creator_id=creator_id,
            max_members=max_members or DEFAULT_MAX_MEMBERS,
        )
        created = await self.repo.create(room)
        # auto-join creator
        await self.member_repo.add(RoomMember(room_id=created.id, user_id=creator_id))
        return self._format(created, 1)

    async def get_all_rooms(self, user_id: int = None, joined: bool = None) -> list[dict]:
        if joined is True and user_id:
            rooms = await self.repo.get_by_user(user_id)
        else:
            rooms = await self.repo.get_all_active()
        result = []
        for room in rooms:
            count = await self.repo.member_count(room.id)
            result.append(self._format(room, count))
        return result

    async def get_room(self, room_id: int) -> dict:
        room = await self.repo.get_by_id(room_id)
        if not room or not room.is_active:
            raise NotFoundError("Room", room_id)
        count = await self.repo.member_count(room_id)
        return self._format(room, count)

    async def join_room(self, room_id: int, user_id: int) -> dict:
        room = await self.repo.get_by_id(room_id)
        if not room or not room.is_active:
            raise NotFoundError("Room", room_id)
        if await self.member_repo.get(room_id, user_id):
            raise AlreadyMemberError()
        count = await self.repo.member_count(room_id)
        if count >= room.max_members:
            raise RoomFullError(room.max_members)
        await self.member_repo.add(RoomMember(room_id=room_id, user_id=user_id))
        return self._format(room, count + 1)

    async def leave_room(self, room_id: int, user_id: int):
        member = await self.member_repo.get(room_id, user_id)
        if not member:
            raise NotMemberError()
        await self.member_repo.delete(member)

    async def kick_member(self, room_id: int, target_user_id: int, requester_id: int, requester_role: str):
        room = await self.repo.get_by_id(room_id)
        if not room or not room.is_active:
            raise NotFoundError("Room", room_id)
        if requester_role != "admin" and room.creator_id != requester_id:
            raise ForbiddenError("Only admin or room creator can kick members")
        member = await self.member_repo.get(room_id, target_user_id)
        if not member:
            raise NotMemberError()
        await self.member_repo.delete(member)

    async def delete_room(self, room_id: int, requester_id: int, requester_role: str):
        room = await self.repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room", room_id)
        if requester_role != "admin":
            raise ForbiddenError("Only admin can delete rooms")
        await self.repo.delete(room)

    async def get_members(self, room_id: int) -> list[int]:
        members = await self.member_repo.get_by_room(room_id)
        return [m.user_id for m in members]

    async def is_member(self, room_id: int, user_id: int) -> bool:
        return await self.member_repo.get(room_id, user_id) is not None
