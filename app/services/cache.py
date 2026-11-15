
from app.database.redis import redis_client


CACHE_TTL = 3600


def get_cached_url(short_code: str) -> str | None:
    """Retrieve an original URL from Redis."""
    return redis_client.get(f"url:{short_code}")


def cache_url(short_code: str, original_url: str) -> None:
    """Store an original URL in Redis with an expiration time."""
    redis_client.setex(
        f"url:{short_code}",
        CACHE_TTL,
        original_url,
    )


def invalidate_url_cache(short_code: str) -> None:
    """Remove a cached URL from Redis."""
    redis_client.delete(f"url:{short_code}")
