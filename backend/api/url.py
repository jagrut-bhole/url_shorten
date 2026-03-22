from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from core.dependencies import get_current_user
from db.database import get_session
from db.models import URL, User, ClickEvent
from schemas.url import (
    URLCreate,
    URLResponse,
    URLStats,
    URLEdit,
    URLEditResponse
)
from lib.cache import CacheKeys, CACHE_TTL, set_cached_data

from lib.cache import get_url_click_count

from utils.generate_code import generate_short_code
from helpers.urlHelper import get_url_from_cache_short_code
from lib.cache import delete_cached_key

router = APIRouter(prefix="/urls", tags=["urls"])

# user sending route and getting the shortened URL in response
@router.post("/shorten",response_model=URLResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(
    body: URLCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
): 
    code = None
    
    for _ in range(5):
        code = generate_short_code()
        if not db.exec(select(URL).where(URL.short_code == code)).first():
            break
        
    url = URL(
        original_url=str(body.original_url),
        short_code=code,
        user_id=current_user.id
    )
    
    db.add(url)
    db.commit()
    db.refresh(url)
    
    return url

# Getting stats for a URL
@router.get("/{short_code}/stats", response_model=URLStats)
def get_url_stats(
    short_code: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    url = db.exec(select(URL).where(
        URL.short_code == short_code,
        URL.user_id == current_user.id
        )).first()
    
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    
    if url.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this URL")
    
    cached_clicks = get_url_click_count(str(url.id))

    return {"total_clicks": cached_clicks if cached_clicks is not None else url.click_count}

# Delete a url
@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(
    short_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        cached_url = get_url_from_cache_short_code(short_code, db)
        
        if not cached_url:
            url = db.exec(select(URL).where(URL.short_code == short_code)).first()
        
        else:
            url = db.get(URL, cached_url.id)
            
            if not url:
                url = db.exec(select(URL).where(URL.short_code == short_code)).first()
                
        if not url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
        
        if url.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this URL")
        
        db.delete(url)
        db.commit()
        delete_cached_key(CacheKeys.url_code(short_code=short_code))
        delete_cached_key(CacheKeys.url_click(url_id=str(url.id)))
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the URL")
        
# edit original URL
@router.patch("/{short_code}", response_model=URLEditResponse, status_code=status.HTTP_200_OK)
def edit_url(
    short_code: str,
    body: URLEdit,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) :
    try:
        cached_url = get_url_from_cache_short_code(short_code, db)
        
        if not cached_url:
            url = db.exec(select(URL).where(URL.short_code == short_code)).first()
        else:
            url = db.get(URL, cached_url.id)
            
            if not url:
                url = db.exec(select(URL).where(URL.short_code == short_code)).first()
        
        if not url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
        
        if url.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to edit this URL")
        
        url.original_url = str(body.new_og_url)
        
        db.commit()
        db.refresh(url)
        payload = {
            "id": str(url.id),
            "original_url": url.original_url,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
        }
        set_cached_data(CacheKeys.url_code(short_code=short_code), payload, CACHE_TTL["URL_CODE"])
        set_cached_data(CacheKeys.url_id(url_id=str(url.id)), payload, CACHE_TTL["URL_ID"])
        
        return URLEditResponse(
            id=url.id,
            new_og_url=url.original_url,
            short_code=url.short_code,
            created_at=url.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error editing URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while editing the URL")
    
# Single URL detail
@router.get("/{short_code}")
def get_url_detail(
    short_code: str,
    db: Session = Depends(get_session),
    current_user : User = Depends(get_current_user)
):
    try:
        cached_url = get_url_from_cache_short_code(short_code , db)
        
        if not cached_url:
            url = db.exec(select(URL).where(URL.short_code == short_code)).first()
            
        else:
            url = db.get(URL, cached_url.id)
            
            if not url:
                url = db.exec(select(URL).where(URL.short_code == short_code)).first()
                
        if not url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
        
        if url.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this URL")
        
        url_click_details = db.exec(select(ClickEvent).where(ClickEvent.url_id == url.id)).all()
        
        if len(url_click_details) > 0:
            click_details = []
            for click in url_click_details:
                click_details.append({
                    "clicked_at": click.clicked_at,
                    "ip_address": click.ip_address,
                    "user_agent": click.user_agent
                })
                
        payload = {
            "id": str(url.id),
            "original_url": url.original_url,
            "short_code": url.short_code,
            "user_id": str(url.user_id) if url.user_id else None,
            "created_at": url.created_at.isoformat() if url.created_at else None,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            "click_count": url.click_count,
            "click_details": click_details if len(url_click_details) > 0 else [],
            "analytics": url_click_details if len(url_click_details) > 0 else [],
        }
        
        return payload
    
    except Exception as e:
        print(f"Error getting URL detail: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while getting the URL detail")
    
# Getting all urls of the user
@router.get("/", response_model=list[URLResponse], status_code=status.HTTP_200_OK)
def get_user_urls(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        user_urls = db.exec(
            select(URL)
            .where(URL.user_id == current_user.id)
            .order_by(URL.created_at.desc())
        ).all()

        return user_urls

    except Exception as e:
        print(f"Error getting user urls: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting user urls",
        )