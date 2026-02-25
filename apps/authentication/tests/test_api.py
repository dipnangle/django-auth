"""Tests for authentication API endpoints."""
import pytest
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestLoginAPI:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/login/"

    def test_login_success(self, verified_user_factory):
        user = verified_user_factory(password="SecurePass123!")
        response = self.client.post(self.url, {
            "email": user.email,
            "password": "SecurePass123!",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data

    def test_login_wrong_password(self, verified_user_factory):
        user = verified_user_factory()
        response = self.client.post(self.url, {
            "email": user.email,
            "password": "WrongPassword!",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["error"]["code"] == "AUTHENTICATION_FAILED"

    def test_login_nonexistent_user(self):
        response = self.client.post(self.url, {
            "email": "nobody@example.com",
            "password": "anything",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unverified_email(self, user_factory):
        user = user_factory(is_email_verified=False)
        user.set_password("SecurePass123!")
        user.save()
        response = self.client.post(self.url, {
            "email": user.email,
            "password": "SecurePass123!",
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"]["code"] == "ACCOUNT_NOT_VERIFIED"

    def test_login_missing_fields(self):
        response = self.client.post(self.url, {"email": "test@example.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRegisterAPI:
    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/register/"

    def test_register_success(self):
        response = self.client.post(self.url, {
            "email": "newreg@example.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert "user_id" in response.data

    def test_register_duplicate_email(self, user_factory):
        user = user_factory()
        response = self.client.post(self.url, {
            "email": user.email,
            "password": "SecurePass123!",
            "first_name": "Dup",
            "last_name": "User",
        })
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_missing_fields(self):
        response = self.client.post(self.url, {"email": "test@example.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefreshAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_refresh_token_success(self, verified_user_factory):
        user = verified_user_factory(password="SecurePass123!")
        login = self.client.post("/api/v1/auth/login/", {
            "email": user.email, "password": "SecurePass123!",
        })
        refresh_token = login.data["refresh_token"]
        response = self.client.post("/api/v1/auth/token/refresh/", {
            "refresh_token": refresh_token
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data

    def test_refresh_invalid_token(self):
        response = self.client.post("/api/v1/auth/token/refresh/", {
            "refresh_token": "invalid.token.here"
        })
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST,
        ]
