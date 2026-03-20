from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
from datetime import datetime

class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None
    
class URLResponse(BaseModel):
    id: UUID
    original_url: HttpUrl
    short_code: str
    created_at: datetime
    click_count: int
    
    class Config:
        from_attributes = True
        
class URLStats(BaseModel):
    total_clicks: int