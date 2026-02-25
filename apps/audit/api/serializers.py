"""Audit log serializers."""
from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = (
            "id", "action", "actor", "actor_email", "actor_role",
            "target_type", "target_id", "target_repr",
            "organization", "ip_address", "user_agent",
            "request_id", "metadata", "status", "created_at",
        )
        read_only_fields = fields
