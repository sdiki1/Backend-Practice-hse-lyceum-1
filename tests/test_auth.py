import pytest
from fastapi import FastAPI, status
from fastapi_users.exceptions import UserNotExists
from httpx import AsyncClient


@pytest.mark.anyio
class TestAuthRegistration:
    """Tests for user registration endpoints."""

    async def test_successful_registration(self, client: AsyncClient) -> None:
        """Test successful user registration."""
        registration_data = {
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890",
            "timezone": "UTC",
        }

        response = await client.post("api/auth/register", json=registration_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["email"] == registration_data["email"]
        assert data["first_name"] == registration_data["first_name"]
        assert data["last_name"] == registration_data["last_name"]
        assert "id" in data
        assert "password" not in data

    async def test_registration_duplicate_email(self, client: AsyncClient) -> None:
        """Test registration with duplicate email."""

        registration_data = {
            "email": "duplicate@example.com",
            "password": "StrongPassword123!",
            "first_name": "First",
            "last_name": "User",
        }
        await client.post("api/auth/register", json=registration_data)

        response = await client.post("api/auth/register", json=registration_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "exist" in response.json()["detail"].lower()

    async def test_registration_invalid_data(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration with invalid data."""

        invalid_data = [
            {"password": "password123", "first_name": "John"},
            {"email": "invalid-email", "password": "password123"},
            {"email": "test@example.com", "password": "123"},
            {"email": "test@example.com"},
        ]

        for data in invalid_data:
            response = await client.post("api/auth/register", json=data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
class TestAuthLogin:
    """Tests for user login endpoints."""

    async def test_successful_login(self, client: AsyncClient) -> None:
        """Test successful user login."""
        register_url = "api/auth/register"
        registration_data = {
            "email": "login_test@example.com",
            "password": "LoginPassword123!",
            "first_name": "Login",
            "last_name": "User",
        }
        await client.post(register_url, json=registration_data)

        login_url = "api/auth/login"
        login_data = {
            "email": "login_test@example.com",
            "password": "LoginPassword123!",
        }

        response = await client.post(login_url, data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert "bearer" in data["token_type"]
        assert len(data["access_token"]) > 0

    async def test_login_invalid_credentials(self, client: AsyncClient) -> None:
        """Test login with invalid credentials."""
        login_url = "api/auth/login"

        invalid_credentials = [
            {"email": "nonexistent@example.com", "password": "wrongpassword"},
            {"email": "nonexistent@example.com", "password": "somepassword"},
        ]

        for credentials in invalid_credentials:
            try:
                response = await client.post(login_url, data=credentials)
            except UserNotExists:
                continue
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.anyio
class TestAuthChangePassword:
    """Tests for password change functionality."""

    async def test_successful_password_change(
        self,
        fastapi_app: FastAPI,
        client: AsyncClient,
    ) -> None:
        """Test successful password change."""

        register_url = "api/auth/register"
        registration_data = {
            "email": "password_change@example.com",
            "password": "OriginalPassword123!",
            "first_name": "Password",
            "last_name": "Change",
        }
        await client.post(register_url, json=registration_data)

        login_url = "api/auth/login"
        login_data = {
            "email": "password_change@example.com",
            "password": "OriginalPassword123!",
        }
        response = await client.post(login_url, data=login_data)
        token = response.json()["access_token"]

        change_url = fastapi_app.url_path_for("change_password")
        change_data = {
            "current_password": "OriginalPassword123!",
            "new_password": "NewStrongPassword456!",
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(change_url, json=change_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["password_changed"] is True
        assert "successfully" in data["message"].lower()

    async def test_password_change_wrong_current_password(
        self,
        fastapi_app: FastAPI,
        client: AsyncClient,
    ) -> None:
        """Test password change with wrong current password."""

        register_url = "api/auth/register"
        registration_data = {
            "email": "wrong_pass@example.com",
            "password": "OriginalPassword123!",
            "first_name": "Wrong",
            "last_name": "Password",
        }
        await client.post(register_url, json=registration_data)

        login_url = "api/auth/login"
        login_data = {
            "email": "wrong_pass@example.com",
            "password": "OriginalPassword123!",
        }
        response = await client.post(login_url, data=login_data)
        token = response.json()["access_token"]

        change_url = fastapi_app.url_path_for("change_password")
        change_data = {
            "current_password": "WrongCurrentPassword",
            "new_password": "NewStrongPassword456!",
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(change_url, json=change_data, headers=headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "current password" in response.json()["detail"].lower()

    async def test_password_change_unauthenticated(
        self,
        fastapi_app: FastAPI,
        client: AsyncClient,
    ) -> None:
        """Test password change without authentication."""
        url = fastapi_app.url_path_for("change_password")

        change_data = {
            "current_password": "somepassword",
            "new_password": "newpassword",
        }

        response = await client.post(url, json=change_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
