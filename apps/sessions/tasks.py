"""Session cleanup tasks."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.sessions.tasks.cleanup_expired_sessions")
def cleanup_expired_sessions():
    """Remove sessions expired more than 90 days ago."""
    from django.utils import timezone
    from datetime import timedelta
    from apps.sessions.models import UserSession

    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = UserSession.objects.filter(expires_at__lt=cutoff).delete()
    logger.info("Cleaned up %d expired sessions", deleted)
    return deleted
