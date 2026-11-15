
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database.session import get_session
from app.main import app


@pytest.fixture
def client():
    """Provide an isolated SQLite database for API integration tests."""

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Do not use TestClient as a context manager here:
    # that would start the real application lifespan.
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()
