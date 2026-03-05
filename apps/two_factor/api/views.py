"""Two-factor authentication API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.core.permissions import IsAuthenticated, IsAccountActive
from apps.two_factor.services import setup_totp, confirm_totp, verify_totp, disable_totp, generate_backup_codes, complete_2fa_login
from apps.authentication.tokens import decode_token


class SetupTOTPView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        result = setup_totp(user=request.user)
        return Response(result)


class ConfirmTOTPView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        code = request.data.get("code")
        result = confirm_totp(user=request.user, code=code)
        return Response(result)


class VerifyTOTPView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        code = request.data.get("code")
        verify_totp(user=request.user, code=code)
        return Response({"message": "2FA verified."})


class CompleteTwoFALoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        partial_token = request.data.get("partial_token")
        code = request.data.get("code")
        payload = decode_token(partial_token, token_type="2fa_pending")
        from apps.users.selectors import get_user_by_id
        user = get_user_by_id(payload["user_id"])
        verify_totp(user=user, code=code)
        result = complete_2fa_login(
            user=user,
            ip_address=getattr(request, "audit_ip", ""),
            user_agent=getattr(request, "audit_user_agent", ""),
        )
        return Response(result)


class DisableTOTPView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        disable_totp(user=request.user, confirmed_by=request.user)
        return Response({"message": "2FA disabled."})


class BackupCodesView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        codes = generate_backup_codes(user=request.user)
        return Response({"backup_codes": codes, "message": "Store these safely. They will not be shown again."})


class VerifyEmailOTPView(APIView):
    """
    POST /api/v1/2fa/verify/email/
    Verify email OTP code after login.
    Body: { "code": "123456", "partial_token": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from apps.two_factor.services import verify_email_otp, complete_2fa_login
        from apps.authentication.tokens import decode_partial_token
        from apps.core.exceptions import TwoFactorInvalid

        code = request.data.get("code", "").strip()
        partial_token = request.data.get("partial_token", "").strip()

        if not code or not partial_token:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "code and partial_token are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = decode_partial_token(partial_token)
            user_id = payload.get("user_id")
        except Exception:
            return Response(
                {"error": {"code": "TOKEN_INVALID", "message": "Invalid or expired session. Please log in again."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        from apps.users.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            verify_email_otp(user=user, code=code)
        except TwoFactorInvalid as e:
            return Response(
                {"error": {"code": "TWO_FACTOR_INVALID", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = complete_2fa_login(
            user=user,
            ip_address=getattr(request, "audit_ip", ""),
            user_agent=getattr(request, "audit_user_agent", ""),
        )
        return Response(result)


class ResendEmailOTPView(APIView):
    """
    POST /api/v1/2fa/resend-code/
    Resend email OTP — user requests a new code.
    Body: { "partial_token": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from apps.two_factor.services import send_email_otp
        from apps.authentication.tokens import decode_partial_token

        partial_token = request.data.get("partial_token", "").strip()
        if not partial_token:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "partial_token is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = decode_partial_token(partial_token)
            user_id = payload.get("user_id")
        except Exception:
            return Response(
                {"error": {"code": "TOKEN_INVALID", "message": "Invalid or expired session. Please log in again."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        from apps.users.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        send_email_otp(user=user, ip_address=getattr(request, "audit_ip", ""))
        return Response({"message": "A new verification code has been sent to your email."})


class SetupEmailOTPView(APIView):
    """
    POST /api/v1/2fa/setup/email/
    Enable email OTP for authenticated user.
    Switches from TOTP to email OTP method.
    """
    def post(self, request):
        from apps.two_factor.services import enable_email_otp
        enable_email_otp(user=request.user)
        return Response({"message": "Email OTP 2FA enabled. You will receive a code by email on each login."})
