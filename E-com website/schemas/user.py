from pydantic import BaseModel, field_validator
from typing import Literal

VALID_ROLES = {"customer", "admin"}


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: Literal["customer", "admin"] = "customer"

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("username cannot be empty")
        return v

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("email cannot be empty")
        return v


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
