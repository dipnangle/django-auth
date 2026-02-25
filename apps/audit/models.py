"""Audit log models."""

from django.db import models
from apps.core.models import BaseModel


class AuditLog(BaseModel):
    """
    Immutable audit trail for all significant platform actions.
    Written via signals and explicit service calls.
    Never soft-deleted — retained per plan's audit_log_retention_days.
    """

    # Who did it
    actor = models.ForeignKey(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="audit_actions",
        db_index=True,
    )
    actor_email = models.EmailField(blank=True)  # Snapshot (in case user deleted)
    actor_role = models.CharField(max_length=50, blank=True)

    # What they did
    action = models.CharField(max_length=100, db_index=True)

    # What it affected
    target_type = models.CharField(max_length=50, blank=True, db_index=True)  # 'user', 'org', 'role' etc
    target_id = models.CharField(max_length=36, blank=True, db_index=True)
    target_repr = models.CharField(max_length=255, blank=True)  # Human-readable snapshot

    # Context
    organization = models.ForeignKey(
        "organizations.Organization",
        null=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=36, blank=True, db_index=True)

    # Extra data
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("success", "Success"), ("failure", "Failure"), ("warning", "Warning")],
        default="success",
    )

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["actor", "created_at"]),
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self):
        return f"{self.actor_email} → {self.action} @ {self.created_at}"
