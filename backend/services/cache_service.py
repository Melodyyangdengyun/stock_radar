import redis
import json
import os
from typing import Optional, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))


class CacheService:
    def __init__(self):
        self.client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = CACHE_TTL):
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    def is_connected(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False


cache_service = CacheService()
