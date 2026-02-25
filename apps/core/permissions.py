"""
Base DRF permission classes.
These enforce role hierarchy and feature access at the view level.
"""

from rest_framework.permissions import BasePermission
from apps.core.exceptions import (
    PermissionDeniedException,
    InsufficientRole,
    FeatureNotAllowed,
    LicenseSuspended,
    AccountSuspended,
)


class IsAuthenticated(BasePermission):
    """Standard auth check with better error messages."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsRoot(BasePermission):
    """Only ROOT users. Used for platform-level operations."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.global_role and request.user.global_role.name == "ROOT"


class IsSuperAdmin(BasePermission):
    """ROOT or SUPERADMIN."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.roles.constants import RoleLevel
        return request.user.get_effective_role_level() <= RoleLevel.SUPERADMIN


class IsAdminPlus(BasePermission):
    """ROOT, SUPERADMIN, or ADMIN_PLUS."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.roles.constants import RoleLevel
        return request.user.get_effective_role_level() <= RoleLevel.ADMIN_PLUS


class IsAdmin(BasePermission):
    """ROOT, SUPERADMIN, ADMIN_PLUS, or ADMIN."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.roles.constants import RoleLevel
        return request.user.get_effective_role_level() <= RoleLevel.ADMIN


class IsActiveOrganizationMember(BasePermission):
    """
    User must be an active member of the current request organization.
    Combines with TenantMiddleware.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request, "organization") or not request.organization:
            return False
        from apps.organizations.selectors import is_active_member
        return is_active_member(request.user, request.organization)


class HasFeature(BasePermission):
    """
    Check that user has a specific feature flag enabled.
    Usage:
        class MyView(APIView):
            permission_classes = [IsAuthenticated, HasFeature]
            required_feature = "reports.export"
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        required_feature = getattr(view, "required_feature", None)
        if not required_feature:
            return True  # No feature required, pass through
        from apps.permissions.selectors import user_has_feature
        return user_has_feature(request.user, required_feature, request.organization)


class OrganizationNotSuspended(BasePermission):
    """
    Rejects requests if the organization's license is suspended.
    """

    def has_permission(self, request, view):
        if not hasattr(request, "organization") or not request.organization:
            return True  # No org context, let other checks handle it
        from apps.plans.selectors import get_active_license
        try:
            license = get_active_license(request.organization)
            if license and license.is_suspended:
                raise LicenseSuspended()
        except LicenseSuspended:
            raise
        except Exception:
            pass
        return True


class IsAccountActive(BasePermission):
    """Ensures user account is not suspended or locked."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_suspended:
            raise AccountSuspended()
        return True


# ─────────────────────────────────────────────
# Composite permission sets (commonly used together)
# ─────────────────────────────────────────────

# Standard authenticated user: active account, active org
StandardUserPermissions = [IsAuthenticated, IsAccountActive, IsActiveOrganizationMember, OrganizationNotSuspended]

# Admin and above
AdminPermissions = [IsAuthenticated, IsAccountActive, IsAdmin, OrganizationNotSuspended]

# Platform-level (ROOT only)
RootOnlyPermissions = [IsAuthenticated, IsAccountActive, IsRoot]
