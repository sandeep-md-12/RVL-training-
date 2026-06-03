from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.exceptions import AlreadyExistsError, NotFoundError, InvalidCredentialsError, InactiveUserError
from datetime import datetime, timezone


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    def _format(self, user: User) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_online": user.is_online,
            "last_seen": user.last_seen,
        }

    async def register(self, username: str, email: str, password: str) -> dict:
        if await self.repo.username_exists(username):
            raise AlreadyExistsError("User", "username")
        if await self.repo.email_exists(email):
            raise AlreadyExistsError("User", "email")
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.user,
        )
        created = await self.repo.create(user)
        return self._format(created)

    async def login(self, username: str, password: str) -> dict:
        user = await self.repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InactiveUserError()
        user.is_online = True
        await self.repo.update(user)
        token = create_access_token({"sub": str(user.id), "role": user.role.value})
        return {"access_token": token, "token_type": "bearer"}

    async def logout(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        user.is_online = False
        user.last_seen = datetime.now(timezone.utc)
        await self.repo.update(user)

    async def set_offline(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if user:
            user.is_online = False
            user.last_seen = datetime.now(timezone.utc)
            await self.repo.update(user)

    async def get_all(self) -> list[dict]:
        users = await self.repo.get_all()
        return [self._format(u) for u in users]

    async def get_by_id(self, user_id: int) -> dict:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return self._format(user)

    async def get_online(self) -> list[dict]:
        users = await self.repo.get_online()
        return [self._format(u) for u in users]
