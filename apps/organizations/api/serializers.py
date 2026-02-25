"""Organization serializers."""
from rest_framework import serializers
from apps.organizations.models import Organization, OrganizationMembership


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id", "name", "slug", "description", "website", "logo_url",
            "custom_domain", "deployment_mode", "is_active", "is_suspended",
            "contact_email", "country", "timezone", "created_at",
        )
        read_only_fields = ("id", "slug", "is_suspended", "created_at")


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", "description", "website", "contact_email", "country", "timezone")


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ("id", "user", "user_email", "user_name", "role", "role_name", "is_active", "joined_at")
        read_only_fields = ("id", "joined_at")
