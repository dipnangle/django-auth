"""Plan and License models."""

from django.db import models
from apps.core.models import BaseModel


class Plan(BaseModel):
    """
    Plan template — defines defaults for a tier.
    e.g. Basic, Pro, Premium, Enterprise.
    ROOT manages these.
    """

    class Tier(models.TextChoices):
        BASIC = "basic", "Basic"
        PRO = "pro", "Pro"
        PREMIUM = "premium", "Premium"
        ENTERPRISE = "enterprise", "Enterprise"

    name = models.CharField(max_length=50, unique=True)
    tier = models.CharField(max_length=20, choices=Tier.choices, unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    price_monthly_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ── User limits ────────────────────────────
    max_superadmins = models.PositiveIntegerField(default=1)
    max_admin_plus = models.PositiveIntegerField(default=2)
    max_admins = models.PositiveIntegerField(default=5)
    max_end_users = models.PositiveIntegerField(default=20)

    # ── Feature flags ─────────────────────────
    # Stored as comma-separated feature strings for simplicity
    # e.g. "reports.export,api.access,dashboard.analytics"
    features_json = models.JSONField(
        default=list,
        help_text="List of enabled feature flag strings for this plan.",
    )

    # ── Other limits ──────────────────────────
    audit_log_retention_days = models.PositiveIntegerField(default=30)
    allow_custom_domain = models.BooleanField(default=False)
    allow_api_access = models.BooleanField(default=False)
    allow_impersonation = models.BooleanField(default=False)
    allow_self_hosted = models.BooleanField(default=False)
    enforce_2fa = models.BooleanField(default=False)

    class Meta:
        db_table = "plans"
        ordering = ["price_monthly_usd"]

    def __str__(self):
        return f"{self.name} ({self.tier})"

    def get_limit_for_role(self, role_name: str) -> int:
        mapping = {
            "SUPERADMIN": self.max_superadmins,
            "ADMIN_PLUS": self.max_admin_plus,
            "ADMIN": self.max_admins,
            "END_USER": self.max_end_users,
        }
        return mapping.get(role_name, 0)


class License(BaseModel):
    """
    Per-organization license — the actual contract.
    Inherits from Plan defaults but can have custom overrides (e.g. special deal).
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="licenses",
        db_index=True,
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="licenses")

    # ── Validity ──────────────────────────────
    is_active = models.BooleanField(default=True, db_index=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True, help_text="Null = lifetime license.")
    is_trial = models.BooleanField(default=False)
    grace_period_ends_at = models.DateTimeField(null=True, blank=True)
    is_suspended = models.BooleanField(default=False, db_index=True)
    suspended_reason = models.TextField(blank=True)

    # ── Per-org overrides (override plan defaults) ──
    # If null, falls back to plan values
    override_max_superadmins = models.PositiveIntegerField(null=True, blank=True)
    override_max_admin_plus = models.PositiveIntegerField(null=True, blank=True)
    override_max_admins = models.PositiveIntegerField(null=True, blank=True)
    override_max_end_users = models.PositiveIntegerField(null=True, blank=True)
    override_features_json = models.JSONField(null=True, blank=True)

    # ── Metadata ──────────────────────────────
    notes = models.TextField(blank=True, help_text="Internal notes about this license deal.")
    created_by = models.ForeignKey(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_licenses",
    )

    class Meta:
        db_table = "licenses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["valid_until", "is_active"]),
        ]

    def __str__(self):
        return f"{self.organization.name} — {self.plan.name}"

    def get_limit_for_role(self, role_name: str) -> int:
        """Get effective limit, respecting per-org overrides."""
        override_map = {
            "SUPERADMIN": self.override_max_superadmins,
            "ADMIN_PLUS": self.override_max_admin_plus,
            "ADMIN": self.override_max_admins,
            "END_USER": self.override_max_end_users,
        }
        override = override_map.get(role_name)
        if override is not None:
            return override
        return self.plan.get_limit_for_role(role_name)

    def get_features(self) -> list:
        """Get effective feature list, respecting override."""
        if self.override_features_json is not None:
            return self.override_features_json
        return self.plan.features_json

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        if self.valid_until is None:
            return False
        return timezone.now() > self.valid_until

    @property
    def is_in_grace_period(self) -> bool:
        from django.utils import timezone
        if self.grace_period_ends_at:
            return timezone.now() <= self.grace_period_ends_at
        return False


class LicenseHistory(BaseModel):
    """Immutable audit trail of license changes."""

    license = models.ForeignKey(License, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=50)  # CREATED, UPGRADED, DOWNGRADED, SUSPENDED, RENEWED
    previous_plan = models.ForeignKey(Plan, null=True, on_delete=models.SET_NULL, related_name="+")
    new_plan = models.ForeignKey(Plan, null=True, on_delete=models.SET_NULL, related_name="+")
    changed_by = models.ForeignKey("users.User", null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    snapshot = models.JSONField(default=dict, help_text="Full license state at time of change.")

    class Meta:
        db_table = "license_history"
        ordering = ["-created_at"]
