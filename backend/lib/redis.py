import redis
from core.config import settings

redis_url = settings.REDIS_URL
r = None

try:
    r = redis.Redis.from_url(
        redis_url,
        retry_on_timeout=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        )
    
    if r.ping():
        print("Connection to Redis successfully!")
        
    else:
        print("Connection to Redis failed!")
        
except redis.exceptions.ConnectionError:
    print("Connection to Redis failed!")

except Exception as e:
    print(f"An error occurred while connecting to Redis: {e}")