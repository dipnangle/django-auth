"""Role serializers."""
from rest_framework import serializers
from apps.roles.models import Role, RoleFeaturePermission


class RoleSerializer(serializers.ModelSerializer):
    requires_2fa = serializers.BooleanField(read_only=True)

    class Meta:
        model = Role
        fields = ("id", "name", "level", "description", "is_global", "requires_2fa")
        read_only_fields = ("id",)


class RoleFeaturePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleFeaturePermission
        fields = ("id", "role", "feature", "is_allowed")
        read_only_fields = ("id",)
