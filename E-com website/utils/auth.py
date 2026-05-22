"""
Password hashing and JWT token utilities.
"""
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# ---------------------------------------------------------------------------
# Configuration — override via environment variables in production
# ---------------------------------------------------------------------------
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production-super-secret-key")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _pre_hash(plain_password: str) -> str:
    """
    SHA-256 digest of the password as a hex string (64 chars / 64 bytes).

    bcrypt silently truncates inputs longer than 72 bytes.  Pre-hashing with
    SHA-256 produces a fixed-length digest that is always within the limit,
    while still preserving the full entropy of arbitrarily long passwords.
    """
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of *plain_password*."""
    return pwd_context.hash(_pre_hash(plain_password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if *plain_password* matches *hashed_password*."""
    return pwd_context.verify(_pre_hash(plain_password), hashed_password)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encode *data* into a signed JWT.

    The token will expire after *expires_delta* (default: ACCESS_TOKEN_EXPIRE_MINUTES).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT.

    Returns the payload dict on success, or None if the token is invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
