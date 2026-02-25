"""Invitation cleanup tasks."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.invitations.tasks.cleanup_expired_invitations")
def cleanup_expired_invitations():
    """Mark expired pending invitations as expired."""
    from django.utils import timezone
    from apps.invitations.models import Invitation

    updated = Invitation.objects.filter(
        status=Invitation.Status.PENDING,
        expires_at__lt=timezone.now(),
    ).update(status=Invitation.Status.EXPIRED)

    logger.info("Marked %d invitations as expired", updated)
    return updated
