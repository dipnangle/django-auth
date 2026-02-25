"""Authentication API views."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from apps.core.middleware import get_current_request
from apps.authentication.services import (
    login_user, logout_user, register_user,
    verify_email, request_password_reset, confirm_password_reset,
    send_verification_email,
)
from apps.authentication.tokens import rotate_refresh_token


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={"type": "object", "properties": {"email": {"type": "string"}, "password": {"type": "string"}}},
    )
    def post(self, request):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Email and password are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = login_user(
            email=email,
            password=password,
            ip_address=getattr(request, "audit_ip", ""),
            user_agent=getattr(request, "audit_user_agent", ""),
        )
        return Response(result)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        logout_user(user=request.user, refresh_token=refresh_token)
        return Response({"message": "Logged out successfully."})


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "refresh_token is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tokens = rotate_refresh_token(refresh_token)
        return Response(tokens)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        required = ["email", "password", "first_name", "last_name"]
        for field in required:
            if not data.get(field):
                return Response(
                    {"error": {"code": "VALIDATION_ERROR", "message": f"{field} is required."}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user = register_user(
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            ip_address=getattr(request, "audit_ip", ""),
        )
        return Response(
            {"message": "Registration successful. Please check your email to verify your account.", "user_id": str(user.id)},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Token is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = verify_email(token=token)
        return Response({"message": "Email verified successfully. You can now log in."})


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()
        if not email:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Email is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.users.selectors import get_user_by_email_or_none
        user = get_user_by_email_or_none(email)
        if user and not user.is_email_verified:
            send_verification_email(user=user)
        return Response({"message": "If your email is registered and unverified, a new link has been sent."})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()
        if not email:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Email is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request_password_reset(email=email, ip_address=getattr(request, "audit_ip", ""))
        return Response({"message": "If your email is registered, a password reset link has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        if not token or not new_password:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "token and new_password are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        confirm_password_reset(token=token, new_password=new_password)
        return Response({"message": "Password reset successfully. Please log in."})
