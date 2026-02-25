from django.urls import path
from apps.plans.api.views import PlanListView, LicenseAssignView

app_name = "plans"

urlpatterns = [
    path("", PlanListView.as_view(), name="plan-list"),
    path("license/assign/", LicenseAssignView.as_view(), name="license-assign"),
]
