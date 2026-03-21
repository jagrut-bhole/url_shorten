from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import uuid


# ── Request bodies (what the client sends) ────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters")
        return v


class DeleteAccountRequest(BaseModel):
    password: str   # require password confirmation before deleting
    
    
class UpdateEmailRequest(BaseModel):
    new_email: EmailStr
    password: str


# ── Response bodies (what we send back) ───────────────────────────────────────

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime
    urls: list = []

    model_config = {"from_attributes": True}   # lets us do UserResponse.model_validate(db_user)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str