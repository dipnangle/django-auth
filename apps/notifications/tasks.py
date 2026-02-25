"""Celery tasks for async email sending."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="notifications.send_email",
)
def send_email_task(self, *, to: str, template: str, context: dict, subject: str = None):
    """
    Async email task with retry logic.
    Retries up to 3 times with exponential backoff on failure.
    """
    from apps.notifications.services import _send_email_sync
    try:
        return _send_email_sync(to=to, template=template, context=context, subject=subject)
    except Exception as exc:
        logger.warning("Email task failed (attempt %d): %s", self.request.retries + 1, str(exc))
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
