from django.urls import path
from apps.organizations.api.views import OrgListCreateView, OrgDetailView, OrgMembersView

app_name = "organizations"

urlpatterns = [
    path("", OrgListCreateView.as_view(), name="org-list"),
    path("<uuid:org_id>/", OrgDetailView.as_view(), name="org-detail"),
    path("<uuid:org_id>/members/", OrgMembersView.as_view(), name="org-members"),
]
