from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class User:
    user_id: str
    username: str
    email: str
    hashed_password: str
    role: str  # "customer" or "admin"
    is_active: bool = True


class UserStore:
    """In-memory user store — no database needed."""

    def __init__(self):
        self._users_by_id: Dict[str, User] = {}
        self._users_by_username: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}

    def add(self, user: User) -> None:
        self._users_by_id[user.user_id] = user
        self._users_by_username[user.username] = user
        self._users_by_email[user.email] = user

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users_by_id.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        return self._users_by_username.get(username)

    def get_by_email(self, email: str) -> Optional[User]:
        return self._users_by_email.get(email)

    def username_exists(self, username: str) -> bool:
        return username in self._users_by_username

    def email_exists(self, email: str) -> bool:
        return email in self._users_by_email


# Singleton store shared across the application
user_store = UserStore()
