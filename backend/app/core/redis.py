import redis
from app.core.config import get_settings

settings = get_settings()


class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.redis_client = redis.Redis(  # pyright: ignore[reportAttributeAccessIssue]
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True
            )
        return cls._instance
    
    def get_client(self):
        return self.redis_client


def get_redis():
    return RedisClient().get_client()
