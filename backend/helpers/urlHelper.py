from db.models import URL
from lib.cache import CACHE_TTL, CacheKeys, get_cached_key, set_cached_data
from sqlmodel import Session, select

NEGATIVE_CACHE_VALUE = "__NOT_FOUND__"

def get_url_from_cache_short_code(short_code: str, db: Session):
    try:
        cache_key = CacheKeys.url_code(short_code=short_code)
    
        cached_url = get_cached_key(cache_key)
    
        if cached_url:
            
            # Negative cache hit
            if cached_url == NEGATIVE_CACHE_VALUE:
                print("Negative cache hit!!!")
                return None
            
            print("Cache hit!!!")
            return cached_url
        else:
            print("No cached URL found")
            print(f"Fetching URL for code {short_code} from database")
            
        url = db.exec(select(URL).where(URL.short_code == short_code)).first()
        
        if not url:
            print("No URL found in database")
            
            set_cached_data(
                cache_key,
                NEGATIVE_CACHE_VALUE,
                CACHE_TTL["NEGATIVE"]
            )
            return None
        
        payload = {
            "id": str(url.id),
            "original_url": url.original_url,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
        }

        set_cached_data(cache_key, payload, CACHE_TTL["URL_CODE"])
        
        return url
    
    except Exception as e:
        print(f"Error getting URL from cache: {e}")
        return None