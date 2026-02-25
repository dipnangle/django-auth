"""Role services."""

import logging
from django.db import transaction
from apps.core.exceptions import InsufficientRole
from apps.roles.hierarchy import can_assign_role

logger = logging.getLogger(__name__)


@transaction.atomic
def assign_role_to_user(*, assigner, user, role, organization=None):
    """Assign a role to a user. Checks hierarchy."""
    if not can_assign_role(assigner=assigner, target_role=role, organization=organization):
        raise InsufficientRole(f"You cannot assign role '{role.name}'.")

    if organization:
        from apps.organizations.services import add_member_to_organization
        add_member_to_organization(organization=organization, user=user, role=role, added_by=assigner)
    else:
        # Global role assignment (ROOT/SUPERADMIN only)
        user.global_role = role
        user.save(update_fields=["global_role", "updated_at"])

    logger.info("Role %s assigned to %s (by %s)", role.name, user.email, assigner.email)
