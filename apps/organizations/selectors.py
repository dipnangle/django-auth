"""Organization selectors."""

from apps.core.exceptions import ResourceNotFound


def get_organization_by_id(org_id: str):
    from apps.organizations.models import Organization
    try:
        return Organization.objects.get(id=org_id)
    except (Organization.DoesNotExist, ValueError):
        raise ResourceNotFound(f"Organization '{org_id}' not found.")


def get_organization_by_slug(slug: str):
    from apps.organizations.models import Organization
    try:
        return Organization.objects.get(slug=slug)
    except Organization.DoesNotExist:
        raise ResourceNotFound(f"Organization '{slug}' not found.")


def get_user_primary_org(user):
    """Get the first active org the user belongs to."""
    from apps.organizations.models import OrganizationMembership
    membership = (
        OrganizationMembership.objects
        .filter(user=user, is_active=True)
        .select_related("organization")
        .first()
    )
    return membership.organization if membership else None


def list_user_organizations(user):
    from apps.organizations.models import Organization, OrganizationMembership
    from apps.roles.constants import RoleLevel
    # ROOT and SUPERADMIN see all organizations
    if user.global_role and user.global_role.level <= RoleLevel.SUPERADMIN:
        return Organization.objects.filter(is_deleted=False).order_by("-created_at")
    # Others see only orgs they are members of
    memberships = (
        OrganizationMembership.objects
        .filter(user=user, is_active=True)
        .select_related("organization", "role")
    )
    return [m.organization for m in memberships]


def is_active_member(user, organization) -> bool:
    from apps.organizations.models import OrganizationMembership
    if user.global_role:  # ROOT/SUPERADMIN are everywhere
        return True
    return OrganizationMembership.objects.filter(
        user=user,
        organization=organization,
        is_active=True,
    ).exists()


def list_organization_members(organization, role=None):
    from apps.organizations.models import OrganizationMembership
    qs = OrganizationMembership.objects.filter(
        organization=organization,
        is_active=True,
    ).select_related("user", "role")
    if role:
        qs = qs.filter(role=role)
    return qs
