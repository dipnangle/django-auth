app_name = "two_factor"

from django.urls import path
from apps.two_factor.api.views import (
    SetupTOTPView, ConfirmTOTPView, VerifyTOTPView,
    CompleteTwoFALoginView, DisableTOTPView, BackupCodesView,
    VerifyEmailOTPView, ResendEmailOTPView, SetupEmailOTPView,
)

urlpatterns = [
    # TOTP (Authenticator App)
    path("setup/totp/", SetupTOTPView.as_view(), name="2fa-setup-totp"),
    path("setup/totp/confirm/", ConfirmTOTPView.as_view(), name="2fa-confirm-totp"),
    path("verify/totp/", VerifyTOTPView.as_view(), name="2fa-verify-totp"),
    path("complete/", CompleteTwoFALoginView.as_view(), name="2fa-complete"),
    path("disable/", DisableTOTPView.as_view(), name="2fa-disable"),
    path("backup-codes/", BackupCodesView.as_view(), name="2fa-backup-codes"),

    # Email OTP
    path("setup/email/", SetupEmailOTPView.as_view(), name="2fa-setup-email"),
    path("verify/email/", VerifyEmailOTPView.as_view(), name="2fa-verify-email"),
    path("resend-code/", ResendEmailOTPView.as_view(), name="2fa-resend-code"),
]
