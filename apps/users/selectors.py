"""
User selectors — all DB read operations for users.
Never put raw ORM queries in views or services; use selectors.
"""

import logging
from django.db.models import Q, Prefetch
from apps.core.exceptions import ResourceNotFound

logger = logging.getLogger(__name__)


def get_user_by_id(user_id: str):
    """Get active user by UUID. Raises ResourceNotFound if not found."""
    from apps.users.models import User
    try:
        return User.objects.select_related("global_role").get(id=user_id)
    except (User.DoesNotExist, ValueError):
        raise ResourceNotFound(f"User with id '{user_id}' not found.")


def get_user_by_email(email: str):
    """Get active user by email. Raises ResourceNotFound if not found."""
    from apps.users.models import User
    try:
        return User.objects.select_related("global_role").get(email__iexact=email)
    except User.DoesNotExist:
        raise ResourceNotFound(f"User with email '{email}' not found.")


def get_user_by_email_or_none(email: str):
    """Get user by email or return None (no exception)."""
    from apps.users.models import User
    return User.objects.select_related("global_role").filter(email__iexact=email).first()


def list_users(
    *,
    organization=None,
    role_name: str = None,
    search: str = None,
    is_active: bool = None,
    is_suspended: bool = None,
    requesting_user=None,
):
    """
    List users with optional filters.
    - If organization is provided, returns only org members
    - requesting_user scope: END_USERs can only see themselves
    """
    from apps.users.models import User
    from apps.roles.constants import RoleLevel

    if organization:
        from apps.organizations.models import OrganizationMembership
        user_ids = OrganizationMembership.objects.filter(
            organization=organization,
            is_active=True,
        ).values_list("user_id", flat=True)
        qs = User.objects.filter(id__in=user_ids).select_related("global_role")
    else:
        qs = User.objects.all().select_related("global_role")

    # Role-based visibility scoping
    if requesting_user:
        user_level = requesting_user.get_effective_role_level(organization)
        if user_level >= RoleLevel.END_USER:
            return qs.filter(id=requesting_user.id)

    if role_name:
        qs = qs.filter(global_role__name=role_name)

    if search:
        qs = qs.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    if is_suspended is not None:
        qs = qs.filter(is_suspended=is_suspended)

    return qs.order_by("-created_at")


def get_user_count_by_role(organization, role) -> int:
    """Count active users in an org with a specific role. Used for plan limit checks."""
    from apps.organizations.models import OrganizationMembership
    return OrganizationMembership.objects.filter(
        organization=organization,
        role=role,
        is_active=True,
        user__is_deleted=False,
    ).count()
