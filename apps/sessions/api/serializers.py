"""Session serializers."""
from rest_framework import serializers
from apps.sessions.models import UserSession


class UserSessionSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = (
            "id", "device_type", "browser", "os",
            "ip_address", "location_country",
            "is_active", "last_active_at", "expires_at",
            "created_at", "is_current",
        )
        read_only_fields = fields

    def get_is_current(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "auth") and request.auth:
            return str(obj.jti) == request.auth.get("jti", "")
        return False
