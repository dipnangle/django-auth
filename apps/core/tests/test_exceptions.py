"""Tests for custom exception handler."""
import pytest
from rest_framework.test import APIRequestFactory
from rest_framework import status
from apps.core.exceptions import (
    custom_exception_handler, ResourceNotFound,
    ValidationError, LicenseLimitExceeded,
    AuthenticationFailed
)


class TestCustomExceptionHandler:
    def _get_context(self):
        factory = APIRequestFactory()
        request = factory.get("/")
        return {"request": request, "view": None}

    def test_resource_not_found_returns_404(self):
        exc = ResourceNotFound("User not found")
        context = self._get_context()
        response = custom_exception_handler(exc, context)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"]["code"] == "NOT_FOUND"
        assert "User not found" in response.data["error"]["message"]

    def test_validation_error_returns_400(self):
        exc = ValidationError("Invalid data")
        response = custom_exception_handler(exc, self._get_context())
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_license_limit_returns_402(self):
        exc = LicenseLimitExceeded("Plan limit reached")
        response = custom_exception_handler(exc, self._get_context())
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED

    def test_auth_failed_returns_401(self):
        exc = AuthenticationFailed()
        response = custom_exception_handler(exc, self._get_context())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_has_standard_shape(self):
        exc = ResourceNotFound("Not found")
        response = custom_exception_handler(exc, self._get_context())
        assert "error" in response.data
        assert "code" in response.data["error"]
        assert "message" in response.data["error"]
