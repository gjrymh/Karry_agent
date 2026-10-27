import redis.asyncio as redis

from src.core.config import get_settings

settings = get_settings()

# 模块级别创建 Redis 客户端实例（连接池由 redis-py 从 URL 自动创建）
_redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8",
)


async def get_redis_client() -> redis.Redis:
    """
    FastAPI Depends 注入用。
    直接返回模块级别的 Redis 客户端实例，不需要每次创建新实例。
    连接池会自动管理连接的获取和归还。
    """
    return _redis_client