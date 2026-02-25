from django.urls import path
from apps.system_config.api.views import SystemConfigListView, SystemConfigUpdateView

app_name = "system_config"

urlpatterns = [
    path("", SystemConfigListView.as_view(), name="config-list"),
    path("<str:key>/", SystemConfigUpdateView.as_view(), name="config-update"),
]
