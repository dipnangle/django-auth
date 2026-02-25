"""
Custom User model.
Uses email as the login identifier (not username).
Designed to work with role hierarchy and multi-tenant org system.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Platform user. Email is the unique identifier.
    Username is removed entirely to avoid confusion.

    Role is NOT stored here — it lives in OrganizationMembership (per-org)
    or as global_role for ROOT/SUPERADMIN who operate platform-wide.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ── Identity ──────────────────────────────
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar_url = models.URLField(blank=True)

    # ── Global role (ROOT / SUPERADMIN only) ──
    # For org-scoped users (ADMIN_PLUS, ADMIN, END_USER),
    # role is in OrganizationMembership
    global_role = models.ForeignKey(
        "roles.Role",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="global_users",
        help_text="Only set for ROOT and SUPERADMIN. Other roles are org-scoped.",
    )

    # ── Status ────────────────────────────────
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Django admin access
    is_email_verified = models.BooleanField(default=False, db_index=True)
    is_suspended = models.BooleanField(default=False, db_index=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suspended_users",
    )

    # ── 2FA ───────────────────────────────────
    is_2fa_enabled = models.BooleanField(default=False, db_index=True)
    is_2fa_enforced = models.BooleanField(
        default=False,
        help_text="Set to True for roles where 2FA is mandatory.",
    )

    # ── Account lockout ───────────────────────
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True, db_index=True)

    # ── Password policy ───────────────────────
    password_changed_at = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(
        default=False,
        help_text="Force password change on next login.",
    )

    # ── Audit ─────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # ── Soft delete ───────────────────────────
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # ── Meta ──────────────────────────────────
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "is_deleted"]),
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["global_role", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    # ── Properties ────────────────────────────

    @property
    def full_name(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email

    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    @property
    def is_root(self) -> bool:
        return self.global_role and self.global_role.name == "ROOT"

    @property
    def is_superadmin(self) -> bool:
        return self.global_role and self.global_role.name == "SUPERADMIN"

    # ── Methods ───────────────────────────────

    def get_effective_role_level(self, organization=None) -> int:
        """
        Returns the numeric level of the user's effective role.
        If org is provided, checks org-scoped role.
        Falls back to global role.
        Lower number = higher privilege.
        """
        from apps.roles.constants import RoleLevel

        if self.global_role:
            return self.global_role.level

        if organization:
            from apps.organizations.models import OrganizationMembership
            try:
                membership = OrganizationMembership.objects.select_related("role").get(
                    user=self,
                    organization=organization,
                    is_active=True,
                )
                return membership.role.level
            except OrganizationMembership.DoesNotExist:
                pass

        return RoleLevel.END_USER  # Most restrictive as fallback

    def get_role_in_org(self, organization):
        """Get the user's role within a specific organization."""
        from apps.organizations.models import OrganizationMembership
        try:
            membership = OrganizationMembership.objects.select_related("role").get(
                user=self,
                organization=organization,
                is_active=True,
            )
            return membership.role
        except OrganizationMembership.DoesNotExist:
            return self.global_role

    def record_login(self, ip_address: str):
        """Update last login metadata."""
        self.last_login_at = timezone.now()
        self.last_login_ip = ip_address
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=["last_login_at", "last_login_ip", "failed_login_attempts", "locked_until", "updated_at"])

    def record_failed_login(self):
        """Increment failed attempts and lock if threshold reached."""
        from django.conf import settings
        from datetime import timedelta

        self.failed_login_attempts += 1
        max_attempts = settings.ACCOUNT_LOCKOUT.get("MAX_FAILED_ATTEMPTS", 5)
        lockout_minutes = settings.ACCOUNT_LOCKOUT.get("LOCKOUT_DURATION_MINUTES", 30)
        progressive = settings.ACCOUNT_LOCKOUT.get("PROGRESSIVE_LOCKOUT", True)

        if self.failed_login_attempts >= max_attempts:
            # Progressive lockout: each lockout doubles the duration
            if progressive:
                multiplier = 2 ** ((self.failed_login_attempts - max_attempts) // max_attempts)
                lockout_minutes = lockout_minutes * multiplier

            self.locked_until = timezone.now() + timedelta(minutes=lockout_minutes)

        self.save(update_fields=["failed_login_attempts", "locked_until", "updated_at"])

    def unlock(self):
        """Manually unlock the account."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=["failed_login_attempts", "locked_until", "updated_at"])

    def suspend(self, suspended_by_user=None):
        """Suspend the user account."""
        self.is_suspended = True
        self.suspended_at = timezone.now()
        self.suspended_by = suspended_by_user
        self.save(update_fields=["is_suspended", "suspended_at", "suspended_by_id", "updated_at"])

    def unsuspend(self):
        """Re-activate a suspended account."""
        self.is_suspended = False
        self.suspended_at = None
        self.suspended_by = None
        self.save(update_fields=["is_suspended", "suspended_at", "suspended_by_id", "updated_at"])

    def soft_delete(self):
        """Soft-delete the user."""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        # Anonymize PII
        self.email = f"deleted_{self.id}@deleted.invalid"
        self.first_name = "Deleted"
        self.last_name = "User"
        self.phone = ""
        self.save(update_fields=[
            "is_deleted", "is_active", "deleted_at",
            "email", "first_name", "last_name", "phone", "updated_at",
        ])
