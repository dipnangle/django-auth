"""Plans Celery tasks."""
from celery import shared_task
import logging
logger = logging.getLogger(__name__)

@shared_task(name="apps.plans.tasks.check_expired_licenses")
def check_expired_licenses():
    from django.utils import timezone
    from apps.plans.models import License
    from apps.plans.services import enter_grace_period

    now = timezone.now()
    expired_licenses = License.objects.filter(
        is_active=True,
        is_suspended=False,
        valid_until__lt=now,
        grace_period_ends_at__isnull=True,
    ).select_related("organization")

    count = 0
    for license in expired_licenses:
        enter_grace_period(organization=license.organization)
        count += 1
        logger.warning("License entered grace period: %s", license.organization.name)

    return count
