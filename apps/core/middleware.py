"""
Core middleware stack:
1. RequestIDMiddleware   — assigns unique ID to every request
2. AuditContextMiddleware — stores request context for audit logging
3. TenantMiddleware       — resolves and attaches current organization
"""

import uuid
import logging
import threading
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

# Thread-local storage for request context (used by audit logging)
_request_context = threading.local()


def get_current_request():
    """Get the current request from thread-local storage."""
    return getattr(_request_context, "request", None)


def get_current_user():
    """Get the current user from thread-local storage."""
    request = get_current_request()
    if request and hasattr(request, "user") and request.user.is_authenticated:
        return request.user
    return None


def get_current_org():
    """Get the current organization from thread-local storage."""
    return getattr(_request_context, "organization", None)


# ─────────────────────────────────────────────
# 1. Request ID Middleware
# ─────────────────────────────────────────────

class RequestIDMiddleware(MiddlewareMixin):
    """
    Assigns a unique UUID to every request.
    Available as request.id and returned in X-Request-ID response header.
    Useful for log correlation across services.
    """

    def process_request(self, request):
        request_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        request.id = request_id
        _request_context.request = request

    def process_response(self, request, response):
        if hasattr(request, "id"):
            response["X-Request-ID"] = request.id
        return response


# ─────────────────────────────────────────────
# 2. Audit Context Middleware
# ─────────────────────────────────────────────

class AuditContextMiddleware(MiddlewareMixin):
    """
    Stores IP address and user agent in thread-local for audit logging.
    Signals/services can call get_current_request() to get this context
    without passing request objects everywhere.
    """

    def process_request(self, request):
        request.audit_ip = self._get_client_ip(request)
        request.audit_user_agent = request.META.get("HTTP_USER_AGENT", "")[:512]
        _request_context.request = request

    def process_response(self, request, response):
        # Log slow requests
        if hasattr(request, "_start_time"):
            duration = time.time() - request._start_time
            if duration > 2.0:
                logger.warning(
                    "Slow request: %s %s took %.2fs",
                    request.method,
                    request.path,
                    duration,
                )
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        request._start_time = time.time()

    @staticmethod
    def _get_client_ip(request):
        """Extract real client IP, respecting reverse proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # X-Forwarded-For can be a comma-separated list; take the first
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip[:45]  # Max IPv6 length


# ─────────────────────────────────────────────
# 3. Tenant Middleware
# ─────────────────────────────────────────────

class TenantMiddleware(MiddlewareMixin):
    """
    Resolves the current organization for every authenticated request.

    Resolution order:
    1. X-Organization-ID header (explicit org selection)
    2. User's default organization (if they only belong to one)
    3. None (ROOT/SUPERADMIN platform-level requests)

    The resolved org is attached to request.organization and stored
    in thread-local for use anywhere in the request lifecycle.
    """

    def process_request(self, request):
        request.organization = None
        _request_context.organization = None

        # Will be resolved after auth (user is set by JWT auth backend)
        # We do lazy resolution in process_view to ensure user is authenticated

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return None

        org = self._resolve_organization(request)
        request.organization = org
        _request_context.organization = org
        return None

    def _resolve_organization(self, request):
        """Determine which org this request is scoped to."""
        from apps.organizations.selectors import get_organization_by_id, get_user_primary_org

        # Explicit header takes priority (for multi-org users)
        org_id = request.META.get("HTTP_X_ORGANIZATION_ID")
        if org_id:
            try:
                org = get_organization_by_id(org_id)
                # Verify user has access to this org
                if self._user_has_org_access(request.user, org):
                    return org
            except Exception:
                pass

        # Fall back to primary org
        try:
            return get_user_primary_org(request.user)
        except Exception:
            return None

    @staticmethod
    def _user_has_org_access(user, org):
        """Check user is a member of the org."""
        from apps.organizations.models import OrganizationMembership
        return OrganizationMembership.objects.filter(
            user=user,
            organization=org,
            is_active=True,
        ).exists()
