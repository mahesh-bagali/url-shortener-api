
from unittest.mock import patch

from app.services.cache import (
    CACHE_TTL,
    cache_url,
    get_cached_url,
    invalidate_url_cache,
)


class TestGetCachedURL:

    @patch("app.services.cache.redis_client")
    def test_get_cached_url_returns_original_url(self, mock_redis):
        mock_redis.get.return_value = "https://www.example.com"

        result = get_cached_url("abc123")

        assert result == "https://www.example.com"
        mock_redis.get.assert_called_once_with("url:abc123")

    @patch("app.services.cache.redis_client")
    def test_get_cached_url_returns_none_when_not_found(self, mock_redis):
        mock_redis.get.return_value = None

        result = get_cached_url("missing1")

        assert result is None
        mock_redis.get.assert_called_once_with("url:missing1")


class TestCacheURL:

    @patch("app.services.cache.redis_client")
    def test_cache_url_stores_url_with_ttl(self, mock_redis):
        cache_url("abc123", "https://www.example.com")

        mock_redis.setex.assert_called_once_with(
            "url:abc123",
            CACHE_TTL,
            "https://www.example.com",
        )

    def test_cache_ttl_is_one_hour(self):
        assert CACHE_TTL == 3600


class TestInvalidateURLCache:

    @patch("app.services.cache.redis_client")
    def test_invalidate_url_cache_deletes_cached_url(self, mock_redis):
        invalidate_url_cache("abc123")

        mock_redis.delete.assert_called_once_with("url:abc123")
