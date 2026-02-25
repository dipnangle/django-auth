"""Invitation API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from apps.core.permissions import IsAuthenticated, IsAdmin, IsAccountActive
from apps.invitations.services import send_invitation, accept_invitation, revoke_invitation, get_invitation_by_token
from apps.roles.selectors import get_role_by_id


class InvitationSendView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAccountActive]

    def post(self, request):
        role = get_role_by_id(request.data.get("role_id"))
        invite = send_invitation(
            invited_by=request.user,
            organization=request.organization,
            role=role,
            email=request.data.get("email"),
            message=request.data.get("message", ""),
        )
        return Response({"id": str(invite.id), "email": invite.email, "status": invite.status}, status=status.HTTP_201_CREATED)


class InvitationPreviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        invite = get_invitation_by_token(token)
        return Response({
            "organization": invite.organization.name,
            "role": invite.role.name,
            "invited_by": invite.invited_by.full_name if invite.invited_by else None,
            "expires_at": invite.expires_at,
            "is_expired": invite.is_expired,
        })


class InvitationAcceptView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        result = accept_invitation(
            token=token,
            first_name=request.data.get("first_name", ""),
            last_name=request.data.get("last_name", ""),
            password=request.data.get("password", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)


class InvitationRevokeView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsAccountActive]

    def delete(self, request, invitation_id):
        revoke_invitation(invitation_id=str(invitation_id), revoked_by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
