from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

# USER MODEL
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    urls: List["URL"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    
# URL MODEL
class URL(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    original_url: str
    short_code: str = Field(unique=True, index=True)
    
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    click_count: int = Field(default=0)
    
    user: Optional["User"] = Relationship(back_populates="urls")
    analytics: List["ClickEvent"] = Relationship(back_populates='url')

# REFRESH TOKEN MODEL
class RefreshToken(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    token: str = Field(unique=True, index=True)
    
    user_id: uuid.UUID = Field(foreign_key="user.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    
    user: User = Relationship(back_populates="refresh_tokens")
    
# Analytics Model -> Click Event
class ClickEvent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    url_id: uuid.UUID = Field(foreign_key="url.id")
    
    clicked_at: datetime = Field(default_factory=datetime.utcnow)
    
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    country: Optional[str] = None
    
    url: URL = Relationship(back_populates="analytics")