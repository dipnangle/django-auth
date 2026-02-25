from django.urls import path
from apps.invitations.api.views import InvitationSendView, InvitationPreviewView, InvitationAcceptView, InvitationRevokeView

app_name = "invitations"

urlpatterns = [
    path("", InvitationSendView.as_view(), name="invitation-send"),
    path("<str:token>/preview/", InvitationPreviewView.as_view(), name="invitation-preview"),
    path("<str:token>/accept/", InvitationAcceptView.as_view(), name="invitation-accept"),
    path("<uuid:invitation_id>/revoke/", InvitationRevokeView.as_view(), name="invitation-revoke"),
]
