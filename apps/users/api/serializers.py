"""User API serializers."""

from rest_framework import serializers
from apps.users.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    """Minimal user info — safe for sharing."""
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "first_name", "last_name", "avatar_url", "role", "created_at"]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.full_name

    def get_role(self, obj):
        request = self.context.get("request")
        org = getattr(request, "organization", None) if request else None
        role = obj.get_role_in_org(org) if org else obj.global_role
        return role.name if role else None


class UserDetailSerializer(serializers.ModelSerializer):
    """Full user detail — for self or admin view."""
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "first_name", "last_name",
            "phone", "avatar_url", "role",
            "is_active", "is_email_verified", "is_suspended",
            "is_2fa_enabled", "is_2fa_enforced",
            "is_locked", "failed_login_attempts",
            "last_login_at", "last_login_ip",
            "password_changed_at", "must_change_password",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "email", "role", "is_email_verified",
            "is_2fa_enabled", "is_2fa_enforced", "is_locked",
            "failed_login_attempts", "last_login_at", "last_login_ip",
            "password_changed_at", "created_at", "updated_at",
        ]

    def get_full_name(self, obj):
        return obj.full_name

    def get_role(self, obj):
        request = self.context.get("request")
        org = getattr(request, "organization", None) if request else None
        role = obj.get_role_in_org(org) if org else obj.global_role
        return role.name if role else None

    def get_is_locked(self, obj):
        return obj.is_locked


class UserUpdateSerializer(serializers.Serializer):
    """Fields a user can update on their own profile."""
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)


class UserCreateSerializer(serializers.Serializer):
    """For admins creating users directly (not via invite)."""
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    role_id = serializers.UUIDField()
    send_invitation = serializers.BooleanField(default=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=10)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data
