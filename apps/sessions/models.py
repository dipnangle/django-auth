"""User session models."""

from django.db import models
from apps.core.models import BaseModel


class UserSession(BaseModel):
    """
    Server-tracked JWT session.
    One record per active refresh token.
    Enables force-logout, device management, and suspicious login detection.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="sessions", db_index=True)
    jti = models.CharField(max_length=36, unique=True, db_index=True, help_text="JWT ID of the refresh token.")

    # Device info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    location_country = models.CharField(max_length=2, blank=True)  # ISO country code

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    last_active_at = models.DateTimeField(auto_now=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "user_sessions"
        ordering = ["-last_active_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["expires_at", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.device_type or 'unknown'} ({self.ip_address})"
