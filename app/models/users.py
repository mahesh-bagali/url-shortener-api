
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Database model representing a registered user."""

    __tablename__ = "users"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    name: str = Field(
        max_length=100,
        nullable=False,
    )

    email: str = Field(
        max_length=255,
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: str = Field(
        max_length=255,
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
