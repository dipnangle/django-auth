"""Role and feature permission models."""

from django.db import models
from apps.core.models import BaseModel
from .constants import RoleLevel


class Role(BaseModel):
    """
    Immutable role definitions.
    These are seeded at startup via migrations — not user-created.
    """

    name = models.CharField(max_length=50, unique=True, db_index=True)
    level = models.PositiveSmallIntegerField(
        choices=RoleLevel.CHOICES,
        unique=True,
        db_index=True,
        help_text="Lower = higher privilege. ROOT=0, END_USER=40.",
    )
    description = models.TextField(blank=True)
    is_global = models.BooleanField(
        default=False,
        help_text="Global roles (ROOT, SUPERADMIN) are not org-scoped.",
    )

    class Meta:
        db_table = "roles"
        ordering = ["level"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name

    @property
    def requires_2fa(self) -> bool:
        return self.level in RoleLevel.MANDATORY_2FA_LEVELS

    @property
    def is_higher_than(self):
        def check(other_role):
            return self.level < other_role.level
        return check

    @property
    def can_manage_level(self) -> int:
        """This role can manage users at this level and below."""
        if self.level == RoleLevel.ROOT:
            return RoleLevel.END_USER
        if self.level == RoleLevel.SUPERADMIN:
            return RoleLevel.END_USER
        if self.level == RoleLevel.ADMIN_PLUS:
            return RoleLevel.END_USER
        if self.level == RoleLevel.ADMIN:
            return RoleLevel.END_USER
        return -1  # END_USER can't manage anyone


class RoleFeaturePermission(BaseModel):
    """
    Default feature permissions for each role.
    These are the baseline — individual users can have overrides.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="feature_permissions",
    )
    feature = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Feature flag string e.g. 'reports.export'",
    )
    is_allowed = models.BooleanField(default=True)

    class Meta:
        db_table = "role_feature_permissions"
        unique_together = [("role", "feature")]
        verbose_name = "Role Feature Permission"

    def __str__(self):
        status = "✓" if self.is_allowed else "✗"
        return f"{self.role.name} {status} {self.feature}"
