"""Impersonation serializers."""
from rest_framework import serializers
from apps.impersonation.models import ImpersonationSession


class ImpersonationSessionSerializer(serializers.ModelSerializer):
    impersonator_email = serializers.CharField(source="impersonator.email", read_only=True)
    target_email = serializers.CharField(source="target.email", read_only=True)

    class Meta:
        model = ImpersonationSession
        fields = (
            "id", "impersonator", "impersonator_email",
            "target", "target_email",
            "organization", "is_active",
            "started_at", "ended_at", "reason", "ip_address",
        )
        read_only_fields = fields


class StartImpersonationSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
