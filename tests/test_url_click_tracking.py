
from fastapi.testclient import TestClient

from app.routers import urls as urls_router
from app.services.security import create_access_token


def create_authenticated_url(client: TestClient) -> tuple[str, int]:
    """Register a user, authenticate directly, and create a URL."""

    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    token = create_access_token(user_id=1)

    client.headers.update(
        {"Authorization": f"Bearer {token}"}
    )

    original_url = "https://example.com/products"

    create_response = client.post(
        "/urls",
        json={"original_url": original_url},
    )

    assert create_response.status_code == 201

    short_code = create_response.json()["short_code"]

    urls_response = client.get("/urls")
    assert urls_response.status_code == 200

    url_record = next(
        url for url in urls_response.json()
        if url["short_code"] == short_code
    )

    return short_code, url_record["id"]


def test_click_count_increments_on_cache_miss(
    client: TestClient,
    monkeypatch,
) -> None:
    """A redirect without a Redis cache entry increments the count."""

    monkeypatch.setattr(
        urls_router,
        "get_cached_url",
        lambda _short_code: None,
    )

    monkeypatch.setattr(
        urls_router,
        "cache_url",
        lambda _short_code, _original_url: None,
    )

    short_code, url_id = create_authenticated_url(client)

    response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/products"

    url_response = client.get(f"/urls/{url_id}")

    assert url_response.status_code == 200
    assert url_response.json()["click_count"] == 1


def test_click_count_increments_on_cache_hit(
    client: TestClient,
    monkeypatch,
) -> None:
    """A redirect using a Redis cache entry increments the count."""

    cached_url = "https://example.com/products"

    monkeypatch.setattr(
        urls_router,
        "get_cached_url",
        lambda _short_code: cached_url,
    )

    short_code, url_id = create_authenticated_url(client)

    response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"] == cached_url

    url_response = client.get(f"/urls/{url_id}")

    assert url_response.status_code == 200
    assert url_response.json()["click_count"] == 1
