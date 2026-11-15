
from app.database.session import get_session
from app.main import app
from app.models import URL
from app.services.security import create_access_token


def register_user(client, email):
    response = client.post(
        "/auth/register",
        json={
            "name": "Analytics User",
            "email": email,
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201

    user_id = response.json()["id"]
    token = create_access_token(user_id)

    return user_id, {"Authorization": f"Bearer {token}"}


def insert_test_urls(user_id, records):
    """Insert URL records into the isolated test database."""

    session_generator = app.dependency_overrides[get_session]()
    session = next(session_generator)

    try:
        for original_url, short_code, click_count in records:
            session.add(
                URL(
                    original_url=original_url,
                    short_code=short_code,
                    user_id=user_id,
                    click_count=click_count,
                )
            )

        session.commit()

    finally:
        session_generator.close()


class TestAnalyticsIntegration:

    def test_analytics_endpoints(self, client):
        user_id, headers = register_user(
            client,
            "analytics@example.com",
        )

        insert_test_urls(
            user_id,
            [
                ("https://example.com/one", "ana001", 10),
                ("https://example.com/two", "ana002", 5),
                ("https://example.com/three", "ana003", 2),
            ],
        )

        # Test analytics summary.
        summary_response = client.get(
            "/analytics/summary",
            headers=headers,
        )

        assert summary_response.status_code == 200
        assert summary_response.json() == {
            "total_urls": 3,
            "total_clicks": 17,
        }

        # Test individual URL analytics and sorting.
        urls_response = client.get(
            "/analytics/urls",
            headers=headers,
        )

        assert urls_response.status_code == 200

        urls = urls_response.json()

        assert len(urls) == 3
        assert [url["click_count"] for url in urls] == [10, 5, 2]
        assert urls[0]["short_code"] == "ana001"

        # Test top URLs with a custom limit.
        top_response = client.get(
            "/analytics/top-urls?limit=2",
            headers=headers,
        )

        assert top_response.status_code == 200

        top_urls = top_response.json()

        assert len(top_urls) == 2
        assert [url["click_count"] for url in top_urls] == [10, 5]

        # Test that a limit below 1 is clamped to 1.
        minimum_limit_response = client.get(
            "/analytics/top-urls?limit=0",
            headers=headers,
        )

        assert minimum_limit_response.status_code == 200
        assert len(minimum_limit_response.json()) == 1

    def test_analytics_only_shows_current_users_data(self, client):
        first_user_id, first_headers = register_user(
            client,
            "firstanalytics@example.com",
        )

        second_user_id, second_headers = register_user(
            client,
            "secondanalytics@example.com",
        )

        insert_test_urls(
            first_user_id,
            [
                ("https://example.com/first", "first01", 8),
            ],
        )

        insert_test_urls(
            second_user_id,
            [
                ("https://example.com/second", "second1", 3),
            ],
        )

        first_summary = client.get(
            "/analytics/summary",
            headers=first_headers,
        )

        second_summary = client.get(
            "/analytics/summary",
            headers=second_headers,
        )

        assert first_summary.json() == {
            "total_urls": 1,
            "total_clicks": 8,
        }

        assert second_summary.json() == {
            "total_urls": 1,
            "total_clicks": 3,
        }

        first_urls = client.get(
            "/analytics/urls",
            headers=first_headers,
        ).json()

        assert len(first_urls) == 1
        assert first_urls[0]["short_code"] == "first01"

    def test_analytics_requires_authentication(self, client):
        response = client.get("/analytics/summary")

        assert response.status_code == 401
