
import os
from collections.abc import Generator

from sqlalchemy.engine import URL
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


# Use Psycopg's pure-Python implementation.
os.environ["PSYCOPG_IMPL"] = "python"


# Configure PostgreSQL DLL path only on Windows.
if os.name == "nt":
    postgres_bin = settings.postgres_libpq_path
    current_path = os.environ.get("PATH", "")

    if postgres_bin not in current_path.split(os.pathsep):
        os.environ["PATH"] = os.pathsep.join(
            [postgres_bin, current_path]
        )


# Build the database URL safely.
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.postgres_user,
    password=settings.postgres_password.get_secret_value(),
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)


# Create the SQLModel database engine.
engine = create_engine(
    database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)


def create_db_and_tables() -> None:
    """Create database tables registered with SQLModel."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Provide a database session for each request."""
    with Session(engine) as session:
        yield session
