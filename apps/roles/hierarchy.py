"""
Role hierarchy enforcement engine.
All role-related permission checks go through here.
This is the most critical piece of the auth system.
"""

import logging
from apps.roles.constants import RoleLevel

logger = logging.getLogger(__name__)


def can_assign_role(*, assigner, target_role, organization=None) -> bool:
    """
    Can `assigner` assign `target_role` to someone?

    Rules:
    - You can only assign roles BELOW your own level
    - ROOT can assign any role
    - SUPERADMIN can assign ADMIN_PLUS and below
    - ADMIN_PLUS can assign ADMIN and below
    - ADMIN can assign END_USER only
    - END_USER cannot assign any role
    """
    assigner_level = assigner.get_effective_role_level(organization)
    target_level = target_role.level

    # Must be strictly higher (lower level number) than the role being assigned
    if assigner_level >= target_level:
        logger.warning(
            "Role assignment denied: %s (level %d) tried to assign level %d",
            assigner.email, assigner_level, target_level,
        )
        return False

    return True


def can_create_user_with_role(*, creator, target_role, organization=None) -> bool:
    """
    Same as can_assign_role but semantically for user creation.
    Alias for clarity in service layer.
    """
    return can_assign_role(assigner=creator, target_role=target_role, organization=organization)


def can_manage_user(*, manager, target) -> bool:
    """
    Can `manager` perform management actions on `target` user?
    (deactivate, suspend, delete, unlock, etc.)

    Rules:
    - You can manage users at a LOWER privilege level than yourself
    - You cannot manage users at your same level or above
    - ROOT can manage anyone
    """
    # Get levels without org context for global checks
    manager_level = manager.get_effective_role_level()
    target_level = target.get_effective_role_level()

    if manager_level >= target_level:
        logger.warning(
            "User management denied: %s (level %d) tried to manage %s (level %d)",
            manager.email, manager_level, target.email, target_level,
        )
        return False

    return True


def can_view_user(*, viewer, target, organization=None) -> bool:
    """
    Can `viewer` see `target` user's profile?
    - Anyone can see themselves
    - ADMIN+ can see users in their org at lower levels
    - ROOT/SUPERADMIN can see anyone
    """
    if str(viewer.id) == str(target.id):
        return True

    viewer_level = viewer.get_effective_role_level(organization)

    if viewer_level <= RoleLevel.ADMIN:
        return True  # Admins can view anyone in their org

    return False


def can_impersonate(*, impersonator, target) -> bool:
    """
    Can `impersonator` impersonate `target`?
    - Only ROOT can impersonate SUPERADMIN
    - ROOT/SUPERADMIN can impersonate ADMIN and below
    - Nobody else can impersonate
    """
    impersonator_level = impersonator.get_effective_role_level()
    target_level = target.get_effective_role_level()

    if impersonator_level >= RoleLevel.ADMIN_PLUS:
        return False  # Only ROOT and SUPERADMIN can impersonate

    if impersonator_level >= target_level:
        return False  # Can only impersonate lower privilege

    return True


def get_assignable_roles(assigner, organization=None):
    """
    Returns the list of Role objects that `assigner` is allowed to assign.
    Used to populate dropdowns in the UI.
    """
    from apps.roles.models import Role
    assigner_level = assigner.get_effective_role_level(organization)
    # Can only assign roles strictly below own level
    return Role.objects.filter(level__gt=assigner_level).order_by("level")


def get_creatable_roles(creator, organization=None):
    """
    Returns roles the creator is allowed to create users with.
    Alias of get_assignable_roles for semantic clarity.
    """
    return get_assignable_roles(creator, organization)


def validate_role_change(*, changer, user, new_role, organization=None) -> bool:
    """
    Validate that `changer` can change `user`'s role to `new_role`.
    - Must be able to manage the user
    - Must be able to assign the new role
    - Must also be above the user's current role (to avoid privilege escalation)
    """
    if not can_manage_user(manager=changer, target=user):
        return False
    if not can_assign_role(assigner=changer, target_role=new_role, organization=organization):
        return False
    return True
