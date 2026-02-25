"""Plan and License serializers."""
from rest_framework import serializers
from apps.plans.models import Plan, License, LicenseHistory


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id", "name", "tier", "description", "is_active",
            "price_monthly_usd", "price_yearly_usd",
            "max_superadmins", "max_admin_plus", "max_admins", "max_end_users",
            "features", "audit_log_retention_days",
            "allow_custom_domain", "allow_api_access", "allow_impersonation",
            "allow_self_hosted", "enforce_2fa",
        )
        read_only_fields = ("id",)


class LicenseSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    plan_tier = serializers.CharField(source="plan.tier", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_in_grace_period = serializers.BooleanField(read_only=True)

    class Meta:
        model = License
        fields = (
            "id", "organization", "plan", "plan_name", "plan_tier",
            "is_active", "valid_from", "valid_until", "is_trial",
            "is_suspended", "suspended_reason",
            "is_expired", "is_in_grace_period",
            "grace_period_ends_at", "notes", "created_at",
        )
        read_only_fields = ("id", "created_at")


class LicenseAssignSerializer(serializers.Serializer):
    organization_id = serializers.UUIDField()
    plan_id = serializers.UUIDField()
    valid_from = serializers.DateField(required=False)
    valid_until = serializers.DateField(required=False)
    is_trial = serializers.BooleanField(default=False)
    notes = serializers.CharField(required=False, allow_blank=True)
