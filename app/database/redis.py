
import redis

from app.config import settings


redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password.get_secret_value() or None,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


def check_redis_connection() -> bool:
    """Check whether Redis is reachable and responding."""
    return bool(redis_client.ping())


def close_redis_connection() -> None:
    """Close the Redis client connection."""
    redis_client.close()
