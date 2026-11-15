
from app.routers import urls as urls_router
from app.services.security import create_access_token


def register_and_authenticate(client, email):
    """Register a test user and return an authorization header."""

    response = client.post(
        "/auth/register",
        json={
            "name": "Integration User",
            "email": email,
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201

    user_id = response.json()["id"]
    token = create_access_token(user_id)

    return {"Authorization": f"Bearer {token}"}


class TestURLCRUD:

    def test_complete_url_crud_lifecycle(self, client, monkeypatch):
        headers = register_and_authenticate(
            client,
            "crud@example.com",
        )

        # Mock cache invalidation so the test does not depend on Redis.
        invalidated_codes = []

        monkeypatch.setattr(
            urls_router,
            "invalidate_url_cache",
            lambda short_code: invalidated_codes.append(short_code),
        )

        # Create a shortened URL.
        create_response = client.post(
            "/urls",
            json={"original_url": "https://www.example.com"},
            headers=headers,
        )

        assert create_response.status_code == 201

        created_data = create_response.json()

        assert created_data["original_url"] == "https://www.example.com"
        assert created_data["short_code"]
        assert created_data["message"] == "URL created successfully"

        short_code = created_data["short_code"]

        # Retrieve all URLs belonging to the user.
        list_response = client.get("/urls", headers=headers)

        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        url_id = list_response.json()[0]["id"]

        # Retrieve the URL by ID.
        get_response = client.get(
            f"/urls/{url_id}",
            headers=headers,
        )

        assert get_response.status_code == 200
        assert get_response.json()["short_code"] == short_code

        # Update the original URL.
        update_response = client.put(
            f"/urls/{url_id}",
            json={"original_url": "https://www.updated-example.com"},
            headers=headers,
        )

        assert update_response.status_code == 200
        assert (
            update_response.json()["original_url"]
            == "https://www.updated-example.com"
        )

        # Delete the URL.
        delete_response = client.delete(
            f"/urls/{url_id}",
            headers=headers,
        )

        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "URL deleted successfully"

        # Confirm that the URL no longer exists.
        final_response = client.get("/urls", headers=headers)

        assert final_response.status_code == 200
        assert final_response.json() == []

        # Cache invalidation should happen after update and delete.
        assert invalidated_codes == [short_code, short_code]


class TestURLOwnership:

    def test_user_cannot_access_another_users_url(self, client):
        first_user_headers = register_and_authenticate(
            client,
            "first@example.com",
        )

        second_user_headers = register_and_authenticate(
            client,
            "second@example.com",
        )

        create_response = client.post(
            "/urls",
            json={"original_url": "https://www.example.com"},
            headers=first_user_headers,
        )

        assert create_response.status_code == 201

        url_id = client.get(
            "/urls",
            headers=first_user_headers,
        ).json()[0]["id"]

        # The second user must not see the first user's URL.
        second_user_list = client.get(
            "/urls",
            headers=second_user_headers,
        )

        assert second_user_list.status_code == 200
        assert second_user_list.json() == []

        # The second user must not retrieve the first user's URL.
        get_response = client.get(
            f"/urls/{url_id}",
            headers=second_user_headers,
        )

        assert get_response.status_code == 404
        assert get_response.json()["detail"] == "URL not found"


class TestURLRedirect:

    def test_redirect_increments_click_count(self, client, monkeypatch):
        headers = register_and_authenticate(
            client,
            "redirect@example.com",
        )

        original_url = "https://www.example.com"

        create_response = client.post(
            "/urls",
            json={"original_url": original_url},
            headers=headers,
        )

        assert create_response.status_code == 201

        short_code = create_response.json()["short_code"]

        # Simulate a cache miss without connecting to Redis.
        monkeypatch.setattr(
            urls_router,
            "get_cached_url",
            lambda code: None,
        )

        cached_items = []

        monkeypatch.setattr(
            urls_router,
            "cache_url",
            lambda code, url: cached_items.append((code, url)),
        )

        # Request the shortened URL without following the redirect.
        redirect_response = client.get(
            f"/{short_code}",
            follow_redirects=False,
        )

        assert redirect_response.status_code == 307
        assert redirect_response.headers["location"] == original_url

        # Confirm that the URL was added to the cache.
        assert cached_items == [(short_code, original_url)]

        # Confirm that the click count increased.
        list_response = client.get("/urls", headers=headers)

        assert list_response.status_code == 200
        assert list_response.json()[0]["click_count"] == 1

    def test_nonexistent_short_code_returns_404(self, client):
        response = client.get("/missing123")

        assert response.status_code == 404
        assert response.json()["detail"] == "Short URL not found"
