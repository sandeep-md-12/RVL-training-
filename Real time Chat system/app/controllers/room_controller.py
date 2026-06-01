from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.services.room_service import RoomService
from app.utils.exceptions import (
    NotFoundError, AlreadyExistsError, RoomFullError,
    AlreadyMemberError, NotMemberError, ForbiddenError
)


class RoomController:
    def __init__(self, db: AsyncSession):
        self.service = RoomService(db)

    async def create_room(self, name: str, creator_id: int, max_members: int = None) -> dict:
        try:
            return await self.service.create_room(name, creator_id, max_members)
        except AlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    async def get_all_rooms(self, user_id: int = None, joined: bool = None) -> list[dict]:
        return await self.service.get_all_rooms(user_id, joined)

    async def get_room(self, room_id: int) -> dict:
        try:
            return await self.service.get_room(room_id)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    async def join_room(self, room_id: int, user_id: int) -> dict:
        try:
            return await self.service.join_room(room_id, user_id)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except AlreadyMemberError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RoomFullError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def leave_room(self, room_id: int, user_id: int):
        try:
            await self.service.leave_room(room_id, user_id)
        except NotMemberError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def kick_member(self, room_id: int, target_user_id: int, requester_id: int, requester_role: str):
        try:
            await self.service.kick_member(room_id, target_user_id, requester_id, requester_role)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except NotMemberError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def delete_room(self, room_id: int, requester_id: int, requester_role: str):
        try:
            await self.service.delete_room(room_id, requester_id, requester_role)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    async def get_members(self, room_id: int) -> list[int]:
        return await self.service.get_members(room_id)

    async def is_member(self, room_id: int, user_id: int) -> bool:
        return await self.service.is_member(room_id, user_id)
