
from urllib.parse import quote

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


redis_password = settings.redis_password.get_secret_value()

if redis_password:
    redis_url = (
        f"redis://:{quote(redis_password, safe='')}"
        f"@{settings.redis_host}:{settings.redis_port}/0"
    )
else:
    redis_url = (
        f"redis://{settings.redis_host}:{settings.redis_port}/0"
    )


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_url,
    headers_enabled=False,
)
