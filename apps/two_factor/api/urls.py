from django.urls import path
from apps.two_factor.api.views import SetupTOTPView, ConfirmTOTPView, VerifyTOTPView, DisableTOTPView, BackupCodesView, CompleteTwoFALoginView

app_name = "two_factor"

urlpatterns = [
    path("setup/", SetupTOTPView.as_view(), name="setup"),
    path("setup/confirm/", ConfirmTOTPView.as_view(), name="confirm"),
    path("verify/", VerifyTOTPView.as_view(), name="verify"),
    path("verify/login/", CompleteTwoFALoginView.as_view(), name="verify-login"),
    path("disable/", DisableTOTPView.as_view(), name="disable"),
    path("backup-codes/", BackupCodesView.as_view(), name="backup-codes"),
]
