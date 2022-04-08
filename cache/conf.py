import json
from typing import Optional
from aioredis import Redis, from_url

from config.conf import RootConfig
from node.uitls import str_to_bool


class RedisCache:
    def __init__(self):
        self.redis_cache: Optional[Redis] = None

    async def init_cache(self):
        self.redis_cache = await from_url(
            RootConfig.REDIS_URL,
            port=RootConfig.REDIS_PORT,
            db=RootConfig.REDIS_DB,
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

    async def hset(self, key, mapping):
        return await self.redis_cache.hset(name=key, mapping=mapping)

    async def hget(self, key: str, field: str):
        return await self.redis_cache.hget(name=key, key=field)

    async def hget_dict(self, key: str, field: str):
        return json.loads(await self.hget(key=key, field=field))

    async def _hm_get_all__value_dicts(self):
        keys = await self.keys('*')
        list_dicts = []

        for key in keys:
            value = await self.redis_cache.hget(name=key, key="value")
            disable = await self.redis_cache.hget(name=key, key="disable")
            value_dict = json.loads(value)

            list_dicts.append(value_dict | {"disable": str_to_bool(disable)})

        return list_dicts

    async def json_to_dict(self, value):
        return json.loads(value)

    async def get_all_node(self):
        return await self._hm_get_all__value_dicts()


redis_cache = RedisCache()
