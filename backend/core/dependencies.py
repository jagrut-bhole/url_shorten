import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from core.security import decode_refresh_token
from db.database import get_session
from db.models import User

# Tells FastAPI to look for "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_session)
):
    """
    Reusable dependency — add to any route that requires authentication.
 
    Usage:
        @router.get("/me")
        def profile(user: User = Depends(get_current_user)):
            ...
    """
    
    token = credentials.credentials
    user_id = decode_refresh_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.get(User, uuid.UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )
        
    return user