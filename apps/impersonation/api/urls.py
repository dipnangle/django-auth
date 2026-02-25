from django.urls import path
from apps.impersonation.api.views import StartImpersonationView, StopImpersonationView

app_name = "impersonation"

urlpatterns = [
    path("start/", StartImpersonationView.as_view(), name="start"),
    path("stop/", StopImpersonationView.as_view(), name="stop"),
]
