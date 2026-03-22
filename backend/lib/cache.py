from core.config import settings
import json
from typing import TypeVar, Optional
from lib.redis import r

T = TypeVar("T")

CACHE_TTL = {
    "USER": 60 * 60,
    "URL_CODE": 60 * 60, # 1 hour for URL code cache
    "URL_CLICK": 60 * 30 * 24,
    "rate_limit": 60 * 30 * 24,
    "NEGATIVE": 10,  # Short TTL for negative cache entries
}

class CacheKeys:
    @staticmethod
    def user(user_id : str):
        return f"user:{user_id}"
    
    @staticmethod
    def url_code(short_code: str):
        return f"url_code:{short_code}"

    @staticmethod
    def url_id(url_id: str):
        return f"url_id:{url_id}"

    @staticmethod
    def rate_limit(user_id:str):
        return f"rate_limit:{user_id}"

    @staticmethod
    def url_click(url_id: str):
        return f"url_click:{url_id}"
    
def get_cached_key(key: str) -> Optional[T]:
    if settings.REDIS_ENABLED is False or r is None:
        return None
    
    try:
        data = r.get(key)

        if not data:
            return None

        if isinstance(data, bytes):
            data = data.decode("utf-8")

        return json.loads(data)
    
    except Exception as e:
        print(f"Error getting cache for key {key}:{e}")
        return None
    

def set_cached_data(
    key: str,
    value: any,
    ttl: int 
) -> None :
    if settings.REDIS_ENABLED is False or r is None:
        return None
    
    try:
        r.setex(key, ttl, json.dumps(value))
        
    except Exception as e:
        print(f"Error setting cache for key {key}:{e}")
        return None
    
def delete_cached_key(key: str) -> None:
    if settings.REDIS_ENABLED is False or r is None:
        return None
    
    try:
        if len(key) > 0:
            r.delete(key)
            
    except Exception as e:
        print(f"Error deleting cache for key {key}:{e}")
        return None
    
def rateLimit(
    user_id: str,
    key: str,
    ttl: int = 3600
):
    try:
        if settings.REDIS_ENABLED is False or r is None:
            return 0

        count = r.incr(key)
        
        if count == 1:
            r.expire(key, ttl)
        
        return count
    
    except Exception as e:
        print(f"Error setting cache for key {key}:{e}")
        return 0


def get_url_click_count(url_id: str) -> Optional[int]:
    if settings.REDIS_ENABLED is False or r is None:
        return None

    key = CacheKeys.url_click(url_id)

    try:
        value = r.get(key)
        if value is None:
            return None
        return int(value)
    except Exception as e:
        print(f"Error getting click count for key {key}:{e}")
        return None


def increment_url_click_count(url_id: str, base_count: int = 0) -> int:
    if settings.REDIS_ENABLED is False or r is None:
        return base_count + 1

    key = CacheKeys.url_click(url_id)

    try:
        # Initialize counter from DB value only once if key doesn't exist.
        r.set(key, base_count, ex=CACHE_TTL["URL_CLICK"], nx=True)
        count = r.incr(key)
        r.expire(key, CACHE_TTL["URL_CLICK"])
        return int(count)
    except Exception as e:
        print(f"Error incrementing click count for key {key}:{e}")
        return base_count + 1