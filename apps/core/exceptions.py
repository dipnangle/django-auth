"""
Custom exception classes and DRF exception handler.
All API errors return a consistent shape:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message",
        "detail": {...}  # optional extra context
    }
}
"""

import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import Http404

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────

class PlatformException(Exception):
    """Base exception for all platform errors."""
    code = "PLATFORM_ERROR"
    message = "An unexpected error occurred."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = None

    def __init__(self, message=None, detail=None):
        self.message = message or self.__class__.message
        self.detail = detail
        super().__init__(self.message)

    def to_dict(self):
        payload = {"code": self.code, "message": self.message}
        if self.detail:
            payload["detail"] = self.detail
        return payload


# ─────────────────────────────────────────────
# Auth Exceptions
# ─────────────────────────────────────────────

class AuthenticationFailed(PlatformException):
    code = "AUTHENTICATION_FAILED"
    message = "Authentication credentials are invalid."
    status_code = status.HTTP_401_UNAUTHORIZED


class TokenExpired(PlatformException):
    code = "TOKEN_EXPIRED"
    message = "Your session has expired. Please log in again."
    status_code = status.HTTP_401_UNAUTHORIZED


class TokenInvalid(PlatformException):
    code = "TOKEN_INVALID"
    message = "The provided token is invalid."
    status_code = status.HTTP_401_UNAUTHORIZED


class AccountLocked(PlatformException):
    code = "ACCOUNT_LOCKED"
    message = "Your account has been locked due to too many failed login attempts."
    status_code = status.HTTP_403_FORBIDDEN


class AccountSuspended(PlatformException):
    code = "ACCOUNT_SUSPENDED"
    message = "Your account has been suspended. Please contact support."
    status_code = status.HTTP_403_FORBIDDEN


class AccountNotVerified(PlatformException):
    code = "ACCOUNT_NOT_VERIFIED"
    message = "Please verify your email address before logging in."
    status_code = status.HTTP_403_FORBIDDEN


class TwoFactorRequired(PlatformException):
    code = "2FA_REQUIRED"
    message = "Two-factor authentication is required to complete this action."
    status_code = status.HTTP_403_FORBIDDEN


class TwoFactorInvalid(PlatformException):
    code = "2FA_INVALID"
    message = "The two-factor authentication code is invalid or expired."
    status_code = status.HTTP_400_BAD_REQUEST


# ─────────────────────────────────────────────
# Permission Exceptions
# ─────────────────────────────────────────────

class PermissionDeniedException(PlatformException):
    code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."
    status_code = status.HTTP_403_FORBIDDEN


class InsufficientRole(PlatformException):
    code = "INSUFFICIENT_ROLE"
    message = "Your role does not allow this action."
    status_code = status.HTTP_403_FORBIDDEN


class FeatureNotAllowed(PlatformException):
    code = "FEATURE_NOT_ALLOWED"
    message = "This feature is not available for your account."
    status_code = status.HTTP_403_FORBIDDEN


# ─────────────────────────────────────────────
# Plan / License Exceptions
# ─────────────────────────────────────────────

class LicenseLimitExceeded(PlatformException):
    code = "LICENSE_LIMIT_EXCEEDED"
    message = "Your plan limit has been reached."
    status_code = status.HTTP_402_PAYMENT_REQUIRED


class LicenseExpired(PlatformException):
    code = "LICENSE_EXPIRED"
    message = "Your organization's license has expired."
    status_code = status.HTTP_402_PAYMENT_REQUIRED


class LicenseSuspended(PlatformException):
    code = "LICENSE_SUSPENDED"
    message = "Your organization's access has been suspended."
    status_code = status.HTTP_403_FORBIDDEN


class PlanFeatureDenied(PlatformException):
    code = "PLAN_FEATURE_DENIED"
    message = "This feature is not available on your current plan."
    status_code = status.HTTP_402_PAYMENT_REQUIRED


# ─────────────────────────────────────────────
# Resource Exceptions
# ─────────────────────────────────────────────

class ResourceNotFound(PlatformException):
    code = "NOT_FOUND"
    message = "The requested resource was not found."
    status_code = status.HTTP_404_NOT_FOUND


class ResourceAlreadyExists(PlatformException):
    code = "ALREADY_EXISTS"
    message = "A resource with this identifier already exists."
    status_code = status.HTTP_409_CONFLICT


class ValidationError(PlatformException):
    code = "VALIDATION_ERROR"
    message = "The provided data is invalid."
    status_code = status.HTTP_400_BAD_REQUEST


# ─────────────────────────────────────────────
# Role / Invitation Exceptions
# ─────────────────────────────────────────────

class InvalidRoleAssignment(PlatformException):
    code = "INVALID_ROLE_ASSIGNMENT"
    message = "You cannot assign this role."
    status_code = status.HTTP_403_FORBIDDEN


class InvitationExpired(PlatformException):
    code = "INVITATION_EXPIRED"
    message = "This invitation has expired."
    status_code = status.HTTP_410_GONE


class InvitationAlreadyUsed(PlatformException):
    code = "INVITATION_ALREADY_USED"
    message = "This invitation has already been accepted."
    status_code = status.HTTP_410_GONE


# ─────────────────────────────────────────────
# Rate Limit
# ─────────────────────────────────────────────

class RateLimitExceeded(PlatformException):
    code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please try again later."
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


# ─────────────────────────────────────────────
# DRF Custom Exception Handler
# ─────────────────────────────────────────────

def custom_exception_handler(exc, context):
    """
    Wraps all DRF exceptions in the standard platform error format.
    """

    # Handle our custom exceptions first
    if isinstance(exc, PlatformException):
        return Response(
            {"error": exc.to_dict()},
            status=exc.status_code,
        )

    # Map Django exceptions
    if isinstance(exc, Http404):
        exc = ResourceNotFound()
        return Response({"error": exc.to_dict()}, status=exc.status_code)

    if isinstance(exc, PermissionDenied):
        exc = PermissionDeniedException()
        return Response({"error": exc.to_dict()}, status=exc.status_code)

    if isinstance(exc, ObjectDoesNotExist):
        exc = ResourceNotFound()
        return Response({"error": exc.to_dict()}, status=exc.status_code)

    # Let DRF handle its own exceptions, then reformat
    response = drf_exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "code": "API_ERROR",
            "message": "An error occurred.",
            "detail": response.data,
        }

        # Extract a better message from DRF errors
        if isinstance(response.data, dict):
            if "detail" in response.data:
                error_payload["message"] = str(response.data["detail"])
                error_payload["detail"] = None
        elif isinstance(response.data, list):
            error_payload["message"] = str(response.data[0]) if response.data else "An error occurred."

        response.data = {"error": error_payload}
        return response

    # Unhandled exception — log it and return 500
    logger.exception("Unhandled exception in API", exc_info=exc)
    return Response(
        {"error": {"code": "SERVER_ERROR", "message": "An internal server error occurred."}},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
