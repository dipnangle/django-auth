"""Two-factor authentication models."""

from django.db import models
from apps.core.models import BaseModel


class TOTPDevice(BaseModel):
    """TOTP device for Google Authenticator-style 2FA."""

    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="totp_device")
    secret = models.CharField(max_length=32)  # Base32 secret
    is_confirmed = models.BooleanField(default=False, db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "totp_devices"

    def __str__(self):
        return f"TOTP: {self.user.email}"


class BackupCode(BaseModel):
    """One-time backup codes for 2FA recovery."""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="backup_codes")
    code_hash = models.CharField(max_length=64, db_index=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "backup_codes"
        indexes = [models.Index(fields=["user", "is_used"])]
