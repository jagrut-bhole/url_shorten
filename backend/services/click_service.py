from sqlmodel import Session
from db.models import ClickEvent, URL
from fastapi import Depends, Request
from db.database import get_session

def log_click(
    url_id: int,
    request: Request,
    db: Session = Depends(get_session)
):
    url = db.get(URL, url_id)
    
    if not url:
        return
    
    url.click_count += 1
    
    forwarded_for = request.headers.get("x-forwarded-for")
    ip_address = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else request.client.host if request.client else None
    )
    
    click_event = ClickEvent(
        url_id=url.id,
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
    )
    
    db.add(url)
    db.add(click_event)
    db.commit()