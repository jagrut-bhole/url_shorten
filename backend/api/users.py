from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.dependencies import get_current_user
from core.security import hash_password, verify_password
from db.database import get_session
from db.models import RefreshToken, User
from schemas.user import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    MessageResponse,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])

# getting user profile
@router.get("/me", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)):
    
    """
    Protected route — requires a valid Bearer token. `get_current_user` does all the JWT validation for us.
    """
    
    return current_user

# password change route
@router.patch("/me/password", response_model=MessageResponse)
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # verifying old password
    if not verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # prevent setting the same password
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="New password must differ from current password")
    
    # Hashing the new password and saveing it to the database
    current_user.password = hash_password(body.new_password)
    db.add(current_user)
    
    # 4. Revoke ALL refresh tokens — force re-login on all devices
    tokens = db.exec(select(RefreshToken).where(RefreshToken.user_id == current_user.id)).all()
    for t in tokens:
        t.is_revoked = True
        db.add(t)
        
        db.commit()
        return MessageResponse(messsage="Password updated. Please log in again.")
    
# Delete account route
@router.delete("/me", response_model=MessageResponse)
def delete_account(
    body: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db : Session = Depends(get_session)
):
    if not verify_password(body.password, current_user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Revoke all refresh tokens
    tokens = db.exec(select(RefreshToken).where(RefreshToken.user_id == current_user.id)).all()
    for t in tokens:
        db.delete(t)
        
    # Delete the user (cascade will handle URLs if configured in DB)
    db.delete(current_user)
    db.commit()
    
    return MessageResponse(message= "Account deleted successfully")