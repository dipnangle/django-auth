"""Organization and membership models."""

from django.db import models
from apps.core.models import BaseModel
from apps.core.validators import validate_organization_name, validate_slug


class Organization(BaseModel):
    """Central tenant anchor. Every piece of data belongs to an org."""

    name = models.CharField(max_length=100, validators=[validate_organization_name])
    slug = models.SlugField(max_length=100, unique=True, db_index=True, validators=[validate_slug])
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    custom_domain = models.CharField(max_length=255, blank=True, unique=True, null=True)

    # Deployment
    deployment_mode = models.CharField(
        max_length=20,
        choices=[("saas", "SaaS"), ("self_hosted", "Self-Hosted")],
        default="saas",
        db_index=True,
    )

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_suspended = models.BooleanField(default=False, db_index=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_reason = models.TextField(blank=True)

    # Contact
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, blank=True)  # ISO 3166-1 alpha-2
    timezone = models.CharField(max_length=50, default="UTC")

    # Creator
    created_by = models.ForeignKey(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_organizations",
    )

    class Meta:
        db_table = "organizations"
        verbose_name = "Organization"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["deployment_mode", "is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def active_license(self):
        """Get the organization's current active license."""
        try:
            return self.licenses.filter(is_active=True).select_related("plan").latest("created_at")
        except Exception:
            return None

    def suspend(self, reason: str = ""):
        from django.utils import timezone
        self.is_suspended = True
        self.suspended_at = timezone.now()
        self.suspended_reason = reason
        self.save(update_fields=["is_suspended", "suspended_at", "suspended_reason", "updated_at"])

    def unsuspend(self):
        self.is_suspended = False
        self.suspended_at = None
        self.suspended_reason = ""
        self.save(update_fields=["is_suspended", "suspended_at", "suspended_reason", "updated_at"])


class OrganizationMembership(BaseModel):
    """
    Links a User to an Organization with a specific role.
    This is the source of truth for org-scoped roles.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="memberships",
        db_index=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
        db_index=True,
    )
    role = models.ForeignKey(
        "roles.Role",
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="added_members",
    )

    class Meta:
        db_table = "organization_memberships"
        unique_together = [("user", "organization")]
        verbose_name = "Organization Membership"
        indexes = [
            models.Index(fields=["organization", "role", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.email} @ {self.organization.name} [{self.role.name}]"
