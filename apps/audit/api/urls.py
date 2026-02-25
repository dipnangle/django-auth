from django.urls import path
from apps.audit.api.views import AuditLogListView

app_name = "audit"

urlpatterns = [
    path("", AuditLogListView.as_view(), name="audit-list"),
]
