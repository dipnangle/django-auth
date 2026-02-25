"""Session API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.permissions import IsAuthenticated, IsAccountActive
from apps.sessions.services import list_active_sessions, revoke_session_by_id, revoke_all_sessions


class SessionListView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        sessions = list_active_sessions(user=request.user)
        return Response([{
            "id": str(s.id), "device_type": s.device_type, "browser": s.browser,
            "os": s.os, "ip_address": s.ip_address, "last_active_at": s.last_active_at,
        } for s in sessions])


class SessionRevokeView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def delete(self, request, session_id):
        revoke_session_by_id(session_id=str(session_id), revoked_by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionRevokeAllView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        count = revoke_all_sessions(user=request.user)
        return Response({"message": f"{count} sessions revoked."})
