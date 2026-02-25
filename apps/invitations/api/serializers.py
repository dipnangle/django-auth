"""Invitation serializers."""
from rest_framework import serializers
from apps.invitations.models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    invited_by_name = serializers.CharField(source="invited_by.full_name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "id", "email", "organization", "organization_name",
            "role", "role_name", "status",
            "invited_by", "invited_by_name",
            "message", "expires_at", "is_expired",
            "accepted_at", "created_at",
        )
        read_only_fields = ("id", "status", "invited_by", "token_hash", "accepted_at", "created_at")


class InvitationSendSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role_id = serializers.UUIDField()
    message = serializers.CharField(required=False, allow_blank=True, max_length=500)


class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=10, write_only=True)
