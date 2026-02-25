"""Plan and license services."""

import logging
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from apps.core.exceptions import LicenseLimitExceeded, LicenseExpired, LicenseSuspended, ResourceNotFound

logger = logging.getLogger(__name__)


def enforce_plan_limit(*, organization, role) -> None:
    """
    Check if adding a user with `role` to `organization` would exceed plan limits.
    Raises LicenseLimitExceeded if limit is exceeded.
    Call this BEFORE creating any user.
    """
    from apps.plans.selectors import get_active_license
    from apps.users.selectors import get_user_count_by_role

    try:
        license = get_active_license(organization)
    except ResourceNotFound:
        raise LicenseLimitExceeded(
            "No active license found for this organization. Please contact support."
        )

    if license.is_suspended:
        raise LicenseSuspended()

    if license.is_expired and not license.is_in_grace_period:
        raise LicenseExpired()

    role_name = role.name
    if role_name in ("ROOT", "SUPERADMIN"):
        return  # Global roles not org-limited

    limit = license.get_limit_for_role(role_name)
    current_count = get_user_count_by_role(organization, role)

    if current_count >= limit:
        raise LicenseLimitExceeded(
            f"Your {license.plan.name} plan allows a maximum of {limit} {role_name} users. "
            f"You currently have {current_count}. Please upgrade your plan to add more."
        )


@transaction.atomic
def assign_license(*, organization, plan, valid_from=None, valid_until=None, is_trial=False, created_by=None, notes=""):
    """Assign a new license to an organization. Deactivates existing license."""
    from apps.plans.models import License, LicenseHistory

    # Deactivate current license
    License.objects.filter(organization=organization, is_active=True).update(is_active=False)

    license = License.objects.create(
        organization=organization,
        plan=plan,
        is_active=True,
        valid_from=valid_from or timezone.now(),
        valid_until=valid_until,
        is_trial=is_trial,
        created_by=created_by,
        notes=notes,
    )

    LicenseHistory.objects.create(
        license=license,
        action="CREATED",
        new_plan=plan,
        changed_by=created_by,
        notes=notes,
        snapshot=_license_snapshot(license),
    )

    logger.info("License assigned to %s: %s", organization.name, plan.name)
    return license


@transaction.atomic
def upgrade_license(*, organization, new_plan, changed_by, notes=""):
    """Upgrade an organization's plan."""
    from apps.plans.models import LicenseHistory
    from apps.plans.selectors import get_active_license

    license = get_active_license(organization)
    old_plan = license.plan

    LicenseHistory.objects.create(
        license=license,
        action="UPGRADED" if new_plan.price_monthly_usd > old_plan.price_monthly_usd else "DOWNGRADED",
        previous_plan=old_plan,
        new_plan=new_plan,
        changed_by=changed_by,
        notes=notes,
        snapshot=_license_snapshot(license),
    )

    license.plan = new_plan
    license.save(update_fields=["plan", "updated_at"])
    logger.info("License upgraded for %s: %s → %s", organization.name, old_plan.name, new_plan.name)
    return license


@transaction.atomic
def suspend_license(*, organization, reason: str, suspended_by):
    from apps.plans.selectors import get_active_license
    license = get_active_license(organization)
    license.is_suspended = True
    license.suspended_reason = reason
    license.save(update_fields=["is_suspended", "suspended_reason", "updated_at"])
    organization.suspend(reason=reason)
    logger.info("License suspended for %s", organization.name)
    return license


@transaction.atomic
def enter_grace_period(*, organization, grace_days: int = 7):
    """Put an org in grace period after license expiry."""
    from apps.plans.selectors import get_active_license
    license = get_active_license(organization)
    license.grace_period_ends_at = timezone.now() + timedelta(days=grace_days)
    license.save(update_fields=["grace_period_ends_at", "updated_at"])
    return license


def _license_snapshot(license) -> dict:
    """Capture license state for history record."""
    return {
        "plan": license.plan.name,
        "valid_from": str(license.valid_from),
        "valid_until": str(license.valid_until),
        "is_trial": license.is_trial,
        "overrides": {
            "max_superadmins": license.override_max_superadmins,
            "max_admin_plus": license.override_max_admin_plus,
            "max_admins": license.override_max_admins,
            "max_end_users": license.override_max_end_users,
        },
    }
