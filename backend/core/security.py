from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    """Turn a plain-text password into a bcrypt hash."""
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Return True if the plain password matches the stored hash."""
    return pwd_context.verify(plain, hashed)

# JWT Helpers Function
def create_access_token(subject: str) -> str:
    """
    Create a short-lived JWT (15 min by default). 'subject' is the user's UUID as a string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access"
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token() -> tuple[str, datetime]:
    """
    Create a random opaque refresh token (stored in DB, not a JWT). Returns (token_string, expiry_datetime).
    """
    
    token = str(uuid.uuid4()) # Generate a random token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return token, expires_at


def decode_refresh_token(token: str) -> Optional[str]:
    """
    Decode a JWT and return the subject (user UUID). Returns None if the token is invalid or expired.
    """
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("type") != "access":
            return None
        
        return payload.get("sub")
    
    except JWTError:
        return None