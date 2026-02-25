"""Permission models."""

from django.db import models
from apps.core.models import BaseModel


class UserPermissionOverride(BaseModel):
    """
    Per-user feature flag override.
    Overrides the role default for a specific user.
    Example: Give one END_USER access to reports.export without changing their role.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="permission_overrides")
    feature = models.CharField(max_length=100, db_index=True)
    is_granted = models.BooleanField()  # True = granted, False = explicitly revoked
    granted_by = models.ForeignKey(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="granted_overrides",
    )
    reason = models.TextField(blank=True)

    class Meta:
        db_table = "user_permission_overrides"
        unique_together = [("user", "feature")]
        verbose_name = "User Permission Override"

    def __str__(self):
        status = "granted" if self.is_granted else "revoked"
        return f"{self.user.email}: {self.feature} {status}"
