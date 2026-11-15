
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database.session import create_db_and_tables
from app.database.redis import (
    check_redis_connection,
    close_redis_connection,
)
from app.models import URL, User
from app.routers.auth import router as auth_router
from app.routers.urls import router as urls_router
from app.routers.analytics import router as analytics_router
from app.services.rate_limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize PostgreSQL and Redis when the application starts."""
    create_db_and_tables()

    try:
        check_redis_connection()
        print("Redis connection successful.")

        yield

    finally:
        close_redis_connection()


app = FastAPI(
    title=settings.app_name,
    description="A REST API for creating and managing shortened URLs.",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Register SlowAPI.
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


@app.get("/", tags=["General"])
async def homepage() -> dict[str, str]:
    """Return a simple welcome message."""
    return {"message": "Welcome to the URL Shortener API"}


@app.get("/health", tags=["General"])
async def health_check() -> dict[str, str]:
    """Report that the API process is responding."""
    return {"status": "ok"}


app.include_router(urls_router)
app.include_router(auth_router)
app.include_router(analytics_router)
