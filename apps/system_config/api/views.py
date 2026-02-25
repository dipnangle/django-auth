"""System config API views — ROOT only."""
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import IsRoot, IsAuthenticated, IsAccountActive
from apps.system_config.models import SystemConfig


class SystemConfigListView(APIView):
    permission_classes = [IsAuthenticated, IsRoot, IsAccountActive]

    def get(self, request):
        configs = SystemConfig.objects.all()
        return Response([{
            "key": c.key,
            "value": "***" if c.is_sensitive else c.value,
            "description": c.description,
        } for c in configs])


class SystemConfigUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsRoot, IsAccountActive]

    def patch(self, request, key):
        config, created = SystemConfig.objects.get_or_create(key=key, defaults={"value": None, "updated_by": request.user})
        config.value = request.data.get("value")
        config.updated_by = request.user
        config.save(update_fields=["value", "updated_by_id", "updated_at"])
        return Response({"key": config.key, "value": config.value})
