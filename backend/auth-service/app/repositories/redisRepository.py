import redis.asyncio as redis
from typing import Optional

from app.config import settings


class RedisRepository:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def set_value(self, key: str, value: str, ttl: int) -> None:
        """Сохраняет значение в Redis с указанным TTL."""
        await self.redis_client.set(key, value, ex=ttl)

    async def get_value(self, key: str) -> Optional[str]:
        """Получает значение по ключу из Redis."""
        return await self.redis_client.get(key)

    async def delete_key(self, key: str) -> None:
        """Удаляет ключ из Redis."""
        await self.redis_client.delete(key)
