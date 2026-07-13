"""Redis 缓存工具。"""
import json
from typing import Any

from redis.asyncio import Redis

from config.cache_config import REDIS_DB, REDIS_HOST, REDIS_PORT

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


async def get_cache(key: str):
    """获取缓存（原始字符串）。"""
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None


async def get_json_cache(key: str):
    """获取缓存并解析为 JSON。"""
    try:
        data = await get_cache(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败: {e}")
        return None


async def set_cache(key: str, value: Any, ex: int = 3600):
    """设置缓存，自动将 dict/list 转 JSON。"""
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await redis_client.setex(key, ex, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False
