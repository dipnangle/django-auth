"""Invitation models."""

from django.db import models
from apps.core.models import BaseModel


class Invitation(BaseModel):
    """
    Invite a user to join an organization with a specific role.
    The invited person sets their own password on accept.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="invitations",
        db_index=True,
    )
    role = models.ForeignKey("roles.Role", on_delete=models.PROTECT)
    email = models.EmailField(db_index=True)
    invited_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
    )

    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    expires_at = models.DateTimeField()

    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="accepted_invitations",
    )
    message = models.TextField(blank=True)  # Optional personal message

    class Meta:
        db_table = "invitations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "organization", "status"]),
            models.Index(fields=["expires_at", "status"]),
        ]

    def __str__(self):
        return f"Invite: {self.email} → {self.organization.name} [{self.role.name}]"

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() > self.expires_at
