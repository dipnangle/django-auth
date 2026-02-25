"""Role selectors."""

from apps.core.exceptions import ResourceNotFound


def get_role_by_id(role_id: str):
    from apps.roles.models import Role
    try:
        return Role.objects.get(id=role_id)
    except (Role.DoesNotExist, ValueError):
        raise ResourceNotFound(f"Role '{role_id}' not found.")


def get_role_by_name(name: str):
    from apps.roles.models import Role
    try:
        return Role.objects.get(name=name.upper())
    except Role.DoesNotExist:
        raise ResourceNotFound(f"Role '{name}' not found.")


def list_roles():
    from apps.roles.models import Role
    return Role.objects.all().order_by("level")


def get_role_feature_defaults(role):
    """Get all feature flags and their default state for a role."""
    from apps.roles.models import RoleFeaturePermission
    return {
        rfp.feature: rfp.is_allowed
        for rfp in RoleFeaturePermission.objects.filter(role=role)
    }
