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
