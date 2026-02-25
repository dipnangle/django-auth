"""Authentication selectors."""

from apps.authentication.models import BlacklistedToken, EmailVerificationToken, PasswordResetToken


def get_valid_email_token(token_hash: str):
    """Get a valid (unused, unexpired) email verification token."""
    from django.utils import timezone
    return EmailVerificationToken.objects.filter(
        token_hash=token_hash,
        is_used=False,
        expires_at__gt=timezone.now(),
    ).select_related("user").first()


def get_valid_password_reset_token(token_hash: str):
    """Get a valid (unused, unexpired) password reset token."""
    from django.utils import timezone
    return PasswordResetToken.objects.filter(
        token_hash=token_hash,
        is_used=False,
        expires_at__gt=timezone.now(),
    ).select_related("user").first()


def is_token_blacklisted_db(jti: str) -> bool:
    """Fallback DB check if Redis is unavailable."""
    return BlacklistedToken.objects.filter(jti=jti).exists()
