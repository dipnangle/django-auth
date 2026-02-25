"""Impersonation models."""

from django.db import models
from apps.core.models import BaseModel


class ImpersonationSession(BaseModel):
    """Tracks active and historical impersonation sessions."""

    impersonator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="impersonation_sessions_as_actor",
    )
    target = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="impersonation_sessions_as_target",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        null=True,
        on_delete=models.SET_NULL,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    impersonation_token = models.CharField(max_length=64, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "impersonation_sessions"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.impersonator.email} → {self.target.email}"
