from apps.core.health import health_check
"""Main URL configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("api/health/", health_check, name="health-check"),
    # Admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.authentication.api.urls", namespace="auth")),
    path("api/v1/users/", include("apps.users.api.urls", namespace="users")),
    path("api/v1/roles/", include("apps.roles.api.urls", namespace="roles")),
    path("api/v1/organizations/", include("apps.organizations.api.urls", namespace="organizations")),
    path("api/v1/plans/", include("apps.plans.api.urls", namespace="plans")),
    path("api/v1/permissions/", include("apps.permissions.api.urls", namespace="permissions")),
    path("api/v1/2fa/", include("apps.two_factor.api.urls", namespace="two_factor")),
    path("api/v1/sessions/", include("apps.sessions.api.urls", namespace="sessions")),
    path("api/v1/invitations/", include("apps.invitations.api.urls", namespace="invitations")),
    path("api/v1/audit/", include("apps.audit.api.urls", namespace="audit")),
    path("api/v1/impersonation/", include("apps.impersonation.api.urls", namespace="impersonation")),
    path("api/v1/system-config/", include("apps.system_config.api.urls", namespace="system_config")),

    # API Schema & Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Health check
    path("api/health/", include("apps.core.health_urls")),

    # Prometheus metrics
    path("", include("django_prometheus.urls")),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
