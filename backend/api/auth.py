from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.dependencies import get_current_user
from core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from db.database import get_session
from db.models import RefreshToken, User
from schemas.user import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Register route
@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_session)):
    # check if user already exists
    existing_user = db.exec(select(User).where(User.email == body.email)).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
        
    # Hashing the user given password
    user = User(
        email=body.email,
        password=hash_password(body.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user) # to get the generated ID and created_at & reload so `created_at` etc. are populated
    
    return user


# Login route
@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_session)):
    # look if user exists
    user = db.exec(select(User).where(User.email == body.email)).first()
    
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access and refresh tokens
    access_token = create_access_token(str(user.id))
    
    refresh_token_str, refresh_expires = create_refresh_token()
    
    db_token = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=refresh_expires
    )
    
    db.add(db_token)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str
    )
    
# Refresh token route
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshRequest, db: Session = Depends(get_session)):
    # finding the refresh token record
    
    db_token = db.exec(
        select(RefreshToken).where(RefreshToken.token == body.refresh_token)
    ).first()
    
    now = datetime.now(timezone.utc)
    
    # validating the token
    if(
        not db_token
        or db_token.is_revoked
        or db_token.expires_at < now
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # rotate the refresh token (invalidate the old one and create a new one)
    db_token.is_revoked = True
    db.add(db_token)
    
    new_access = create_access_token(str(db_token.user_id))
    new_refresh_str , new_refresh_exp = create_refresh_token()
    
    new_db_token = RefreshToken(
        token=new_refresh_str,
        user_id=db_token.user_id,
        expires_at=new_refresh_exp
    )
    
    db.add(new_db_token)
    db.commit()
    
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh_str
    )

# Logout route
@router.post("/logout", response_model=MessageResponse)
def logout(body: RefreshRequest, db: Session = Depends(get_session)):
    """Revoke the refresh token — access token expires on its own (15 min)."""
    
    db_token = db.exec(
        select(RefreshToken).where(RefreshToken.token == body.refresh_token)
    ).first()
    
    if db_token and not db_token.is_revoked:
        db_token.is_revoked = True
        db.add(db_token)
        db.commit()
 
    # Always return success — don't leak whether the token existed
    return MessageResponse(message="Logged out successfully")