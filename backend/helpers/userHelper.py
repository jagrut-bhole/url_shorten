from db.models import  User
from lib.cache import CACHE_TTL, CacheKeys, get_cached_key, set_cached_data
from sqlmodel import Session, select

def get_user_from_cache(user_id: str, db: Session):
    try:
        cache_key = CacheKeys.user(user_id=user_id)
        
        cache_user = get_cached_key(cache_key)
        
        if cache_user:
            print("Cache hit!!!")
            return User.model_validate(cache_user)
        else:
            print("No cached user found")
            print(f"Fetching user {user_id} from database")
            
        user = db.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            print("No user found in database")
            return None
        
        payload = {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        
        set_cached_data(cache_key, payload, CACHE_TTL["USER"])
        
        return user
    
    except Exception as e:
        print(f"Error getting user from cache: {e}")
        return None