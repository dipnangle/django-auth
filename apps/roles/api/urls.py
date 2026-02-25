from django.urls import path
from apps.roles.api.views import RoleListView, AssignRoleView

app_name = "roles"

urlpatterns = [
    path("", RoleListView.as_view(), name="role-list"),
    path("assign/", AssignRoleView.as_view(), name="assign-role"),
]
