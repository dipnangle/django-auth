"""Audit log cleanup tasks."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.audit.tasks.cleanup_expired_logs")
def cleanup_expired_logs():
    """Remove audit logs past their retention period based on plan."""
    from django.utils import timezone
    from datetime import timedelta
    from apps.audit.models import AuditLog
    from apps.organizations.models import Organization
    from apps.plans.selectors import get_active_license

    total_deleted = 0
    for org in Organization.objects.filter(is_active=True):
        try:
            license = get_active_license(org)
            if license is None:
                retention_days = 30  # default
            elif license.plan.audit_log_retention_days == 0:
                continue  # unlimited — skip
            else:
                retention_days = license.plan.audit_log_retention_days

            cutoff = timezone.now() - timedelta(days=retention_days)
            deleted, _ = AuditLog.objects.filter(organization=org, created_at__lt=cutoff).delete()
            if deleted:
                total_deleted += deleted
                logger.info("Deleted %d audit logs for org %s (retention=%dd)", deleted, org.name, retention_days)
        except Exception as e:
            logger.error("Error cleaning audit logs for org %s: %s", org.id, e)

    logger.info("Total audit logs cleaned: %d", total_deleted)
    return total_deleted
