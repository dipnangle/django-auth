from django.urls import path
from apps.sessions.api.views import SessionListView, SessionRevokeView, SessionRevokeAllView

app_name = "sessions"

urlpatterns = [
    path("", SessionListView.as_view(), name="session-list"),
    path("<uuid:session_id>/", SessionRevokeView.as_view(), name="session-revoke"),
    path("revoke-all/", SessionRevokeAllView.as_view(), name="session-revoke-all"),
]
