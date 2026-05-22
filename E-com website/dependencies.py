"""
Reusable FastAPI dependency functions for authentication and authorisation.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.user import User, user_store
from utils.auth import decode_access_token

# FastAPI will look for a Bearer token in the Authorization header.
# tokenUrl must match the /auth/token endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Decode the JWT and return the matching User.

    Raises HTTP 401 if the token is missing, invalid, expired, or the user
    no longer exists / is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = user_store.get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure the authenticated user has the 'admin' role.

    Raises HTTP 403 if the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
