"""Plan selectors."""

from apps.core.exceptions import ResourceNotFound


def get_active_license(organization):
    from apps.plans.models import License
    try:
        return License.objects.filter(
            organization=organization,
            is_active=True,
        ).select_related("plan").latest("created_at")
    except License.DoesNotExist:
        raise ResourceNotFound(f"No active license for organization '{organization.name}'.")


def is_feature_enabled(organization, feature: str) -> bool:
    """Check if a feature is enabled for an organization's plan."""
    try:
        license = get_active_license(organization)
        return feature in license.get_features()
    except ResourceNotFound:
        return False


def get_role_limit(organization, role_name: str) -> int:
    """Get the max user count for a role in an org."""
    try:
        license = get_active_license(organization)
        return license.get_limit_for_role(role_name)
    except ResourceNotFound:
        return 0


def list_plans():
    from apps.plans.models import Plan
    return Plan.objects.filter(is_active=True).order_by("price_monthly_usd")
