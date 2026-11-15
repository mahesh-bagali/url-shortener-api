
class TestUserRegistration:

    def test_register_user_successfully(self, client):
        response = client.post(
            "/auth/register",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "password_hash" not in data
        assert "password" not in data

    def test_duplicate_email_is_rejected(self, client):
        payload = {
            "name": "Test User",
            "email": "duplicate@example.com",
            "password": "StrongPassword123!",
        }

        first_response = client.post("/auth/register", json=payload)
        second_response = client.post("/auth/register", json=payload)

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json()["detail"] == "Email is already registered"

    def test_register_with_invalid_email_is_rejected(self, client):
        response = client.post(
            "/auth/register",
            json={
                "name": "Test User",
                "email": "not-an-email",
                "password": "StrongPassword123!",
            },
        )

        assert response.status_code == 422

    def test_register_with_short_password_is_rejected(self, client):
        response = client.post(
            "/auth/register",
            json={
                "name": "Test User",
                "email": "short@example.com",
                "password": "123",
            },
        )

        assert response.status_code == 422


class TestUserLogin:

    def test_login_with_correct_credentials(self, client):
        client.post(
            "/auth/register",
            json={
                "name": "Login User",
                "email": "login@example.com",
                "password": "StrongPassword123!",
            },
        )

        response = client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Login successful"
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert data["user"]["email"] == "login@example.com"

    def test_login_with_wrong_password_is_rejected(self, client):
        client.post(
            "/auth/register",
            json={
                "name": "Login User",
                "email": "wrongpass@example.com",
                "password": "StrongPassword123!",
            },
        )

        response = client.post(
            "/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_with_unregistered_email_is_rejected(self, client):
        response = client.post(
            "/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert response.status_code == 401


class TestUserProfile:

    def test_get_profile_with_valid_token(self, client):
        client.post(
            "/auth/register",
            json={
                "name": "Profile User",
                "email": "profile@example.com",
                "password": "StrongPassword123!",
            },
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "profile@example.com",
                "password": "StrongPassword123!",
            },
        )

        token = login_response.json()["access_token"]

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Profile User"
        assert response.json()["email"] == "profile@example.com"

    def test_get_profile_without_token_is_rejected(self, client):
        response = client.get("/auth/me")

        assert response.status_code == 401
