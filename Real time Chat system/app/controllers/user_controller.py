from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.services.user_service import UserService
from app.utils.exceptions import AlreadyExistsError, NotFoundError, InvalidCredentialsError, InactiveUserError


class UserController:
    def __init__(self, db: AsyncSession):
        self.service = UserService(db)

    async def register(self, username: str, email: str, password: str) -> dict:
        try:
            return await self.service.register(username, email, password)
        except AlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    async def login(self, username: str, password: str) -> dict:
        try:
            return await self.service.login(username, password)
        except InvalidCredentialsError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        except InactiveUserError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    async def logout(self, user_id: int):
        try:
            await self.service.logout(user_id)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    async def get_all(self) -> list[dict]:
        return await self.service.get_all()

    async def get_by_id(self, user_id: int) -> dict:
        try:
            return await self.service.get_by_id(user_id)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    async def get_online(self) -> list[dict]:
        return await self.service.get_online()
