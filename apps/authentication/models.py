"""Authentication models."""

from django.db import models
from apps.core.models import BaseModel


class BlacklistedToken(BaseModel):
    """
    Persistent blacklist for JWT tokens.
    Redis is primary store; this is a backup and for audit purposes.
    """
    jti = models.CharField(max_length=36, unique=True, db_index=True)
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="blacklisted_tokens")
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True, default="logout")

    class Meta:
        db_table = "blacklisted_tokens"

    def __str__(self):
        return f"{self.jti} ({self.reason})"


class EmailVerificationToken(BaseModel):
    """Token for email address verification."""

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="email_verification_token",
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "email_verification_tokens"

    def __str__(self):
        return f"Verify: {self.user.email}"

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() > self.expires_at


class PasswordResetToken(BaseModel):
    """Token for password reset flow."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    requested_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "password_reset_tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reset: {self.user.email}"

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() > self.expires_at
