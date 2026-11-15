
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    app_name: str = "URL Shortener API"
    debug: bool = False

    # PostgreSQL configuration
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "url_shortener_db"

    postgres_libpq_path: str = (
        r"C:\Program Files\PostgreSQL\18\bin"
    )

    # JWT configuration
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: SecretStr = SecretStr("")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
