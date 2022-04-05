import json
from typing import Optional
from aioredis import Redis, from_url


class RedisCache:

    def __init__(self):
        self.redis_cache: Optional[Redis] = None

    async def init_cache(self):
        self.redis_cache = await from_url(
            "redis://redis",
            port=6379,
            db=0,
        )

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value):
        return await self.redis_cache.set(key, value)

    async def get(self, key):
        return await self.redis_cache.get(key)

    async def delete(self, key):
        return await self.redis_cache.delete(key)

    async def close(self):
        await self.redis_cache.close()

    async def _value_to_list_dicts(self):
        keys = await self.redis_cache.keys('*')
        values = [json.loads(await self.redis_cache.get(key)) for key in keys]
        return values

    async def get_all_dicts(self):
        return await self._value_to_list_dicts()

    async def json_to_dict(self, value):
        return json.loads(value)


redis_cache = RedisCache()
