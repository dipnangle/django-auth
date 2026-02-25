"""Impersonation API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import IsAuthenticated, IsSuperAdmin, IsAccountActive
from apps.impersonation.services import start_impersonation, stop_impersonation
from apps.users.selectors import get_user_by_id


class StartImpersonationView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin, IsAccountActive]

    def post(self, request):
        target = get_user_by_id(request.data.get("user_id"))
        result = start_impersonation(
            impersonator=request.user,
            target=target,
            organization=request.organization,
            reason=request.data.get("reason", ""),
            ip=getattr(request, "audit_ip", ""),
        )
        return Response(result)


class StopImpersonationView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        stop_impersonation(impersonator=request.user)
        return Response({"message": "Impersonation ended."})
