from src.db.redis import cache_client
import json
from pydantic.json import pydantic_encoder

CACHE_EXPIRY = 3600

async def get_cached_data(key: str) -> dict | list | None:
    cached_value = await cache_client.get(key)

    if cached_value:
        return json.loads(cached_value)
    
    return None

async def set_cache_data(key: str, data: dict | list, expire: int = CACHE_EXPIRY) -> None:
    serialized_data = json.dumps(data, default=pydantic_encoder)
    await cache_client.set(name=key, value=serialized_data, ex=expire)

async def invalidate_cache(key: str) -> None:
    await cache_client.delete(key)
