from django.urls import path
from apps.permissions.api.views import FeatureListView, PermissionOverrideView

app_name = "permissions"

urlpatterns = [
    path("features/", FeatureListView.as_view(), name="feature-list"),
    path("override/", PermissionOverrideView.as_view(), name="permission-override"),
]
