"""
Authentication routes:
  POST /auth/register  — create a new user account
  POST /auth/token     — exchange credentials for a JWT
"""
import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from models.user import User, user_store
from schemas.user import UserRegister, UserResponse, TokenResponse
from utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegister) -> UserResponse:
    """
    Register a new user.

    - **username** must be unique.
    - **email** must be unique.
    - **password** is stored as a bcrypt hash — never in plain text.
    - **role** is either ``"customer"`` (default) or ``"admin"``.
    """
    if user_store.username_exists(data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    if user_store.email_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        user_id=str(uuid.uuid4()),
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    user_store.add(user)

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )


@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    """
    Obtain a JWT access token.

    Accepts **OAuth2 form data** (``username`` + ``password``).
    The returned token expires after **30 minutes**.
    """
    user = user_store.get_by_username(form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    # Store user_id (as "sub") and role inside the token payload
    token = create_access_token({"sub": user.user_id, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer")
