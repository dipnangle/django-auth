"""Audit log API views — read-only."""
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import IsAuthenticated, IsAdmin, IsAccountActive
from apps.core.pagination import StandardResultsPagination
from apps.audit.models import AuditLog


class AuditLogListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAccountActive]

    def get(self, request):
        qs = AuditLog.objects.all()
        if request.organization:
            qs = qs.filter(organization=request.organization)
        if request.query_params.get("action"):
            qs = qs.filter(action=request.query_params["action"])
        if request.query_params.get("actor_id"):
            qs = qs.filter(actor_id=request.query_params["actor_id"])
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response([{
            "id": str(l.id), "action": l.action, "actor_email": l.actor_email,
            "target_type": l.target_type, "target_repr": l.target_repr,
            "status": l.status, "ip_address": l.ip_address, "created_at": l.created_at,
        } for l in page])
