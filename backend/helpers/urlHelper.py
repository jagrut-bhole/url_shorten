from db.models import URL
from lib.cache import CACHE_TTL, CacheKeys, get_cached_key, set_cached_data
from sqlmodel import Session, select

def get_url_from_cache_short_code(short_code: str, db: Session):
    try:
        cache_key = CacheKeys.url_code(short_code=short_code)
    
        cached_url = get_cached_key(cache_key)
    
        if cached_url:
            return URL.model_validate(cached_url)
        else:
            print("No cached URL found")
            print(f"Fetching URL for code {short_code} from database")
            
        url = db.exec(select(URL).where(URL.short_code == short_code)).first()
        
        if not url:
            print("No URL found in database")
            return None
        
        payload = {
            "id": str(url.id),
            "original_url": url.original_url,
            "short_code": url.short_code,
            "user_id": str(url.user_id) if url.user_id else None,
            "created_at": url.created_at.isoformat() if url.created_at else None,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            "click_count": url.click_count,
        }

        set_cached_data(cache_key, payload, CACHE_TTL["URL_CODE"])
        
        return url
    
    except Exception as e:
        print(f"Error getting URL from cache: {e}")
        return None