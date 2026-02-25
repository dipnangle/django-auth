"""Authentication cleanup tasks."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.authentication.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """Remove used/expired email verification and password reset tokens."""
    from django.utils import timezone
    from apps.authentication.models import EmailVerificationToken, PasswordResetToken, BlacklistedToken

    now = timezone.now()
    ev_deleted, _ = EmailVerificationToken.objects.filter(expires_at__lt=now).delete()
    pr_deleted, _ = PasswordResetToken.objects.filter(expires_at__lt=now).delete()
    bl_deleted, _ = BlacklistedToken.objects.filter(expires_at__lt=now).delete()

    logger.info(
        "Cleaned tokens: %d email-verify, %d password-reset, %d blacklisted",
        ev_deleted, pr_deleted, bl_deleted,
    )
    return ev_deleted + pr_deleted + bl_deleted
