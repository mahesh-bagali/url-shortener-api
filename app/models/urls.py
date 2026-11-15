
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class URL(SQLModel, table=True):
    """Database model representing a shortened URL."""

    __tablename__ = "urls"

    id: int | None = Field(default=None, primary_key=True)

    original_url: str = Field(
        max_length=2048,
        nullable=False,
    )

    short_code: str = Field(
        min_length=6,
        max_length=8,
        unique=True,
        index=True,
        nullable=False,
    )

    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    click_count: int = Field(
        default=0,
        nullable=False,
    )
