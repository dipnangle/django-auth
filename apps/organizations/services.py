"""Organization services."""

import logging
from django.db import transaction
from apps.core.exceptions import ResourceNotFound, ResourceAlreadyExists, InsufficientRole
from apps.core.utils import generate_unique_slug

logger = logging.getLogger(__name__)


@transaction.atomic
def create_organization(*, name: str, created_by, deployment_mode: str = "saas", **kwargs):
    from apps.organizations.models import Organization
    from apps.roles.constants import RoleLevel

    if created_by.get_effective_role_level() > RoleLevel.SUPERADMIN:
        raise InsufficientRole("Only ROOT or SUPERADMIN can create organizations.")

    slug = generate_unique_slug(name, Organization)
    org = Organization.objects.create(
        name=name,
        slug=slug,
        deployment_mode=deployment_mode,
        created_by=created_by,
        **kwargs,
    )
    logger.info("Organization created: %s (by: %s)", org.name, created_by.email)
    return org


@transaction.atomic
def add_member_to_organization(*, organization, user, role, added_by=None):
    from apps.organizations.models import OrganizationMembership
    from apps.roles.constants import RoleLevel

    if OrganizationMembership.objects.filter(user=user, organization=organization).exists():
        # Update role instead
        membership = OrganizationMembership.objects.get(user=user, organization=organization)
        membership.role = role
        membership.is_active = True
        membership.save(update_fields=["role", "is_active", "updated_at"])
        return membership

    return OrganizationMembership.objects.create(
        user=user,
        organization=organization,
        role=role,
        added_by=added_by,
        is_active=True,
    )


@transaction.atomic
def remove_member_from_organization(*, organization, user, removed_by):
    from apps.organizations.models import OrganizationMembership
    from apps.roles.hierarchy import can_manage_user

    if not can_manage_user(manager=removed_by, target=user):
        raise InsufficientRole("You cannot remove this user.")

    OrganizationMembership.objects.filter(
        user=user, organization=organization
    ).update(is_active=False)
