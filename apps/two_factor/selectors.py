"""Two-factor authentication selectors."""

from apps.two_factor.models import TOTPDevice, BackupCode


def get_totp_device(user):
    """Get user's TOTP device or None."""
    return TOTPDevice.objects.filter(user=user).first()


def get_confirmed_totp_device(user):
    """Get confirmed TOTP device or None."""
    return TOTPDevice.objects.filter(user=user, is_confirmed=True).first()


def has_active_2fa(user) -> bool:
    """Check if user has confirmed 2FA setup."""
    return TOTPDevice.objects.filter(user=user, is_confirmed=True).exists()


def get_unused_backup_codes_count(user) -> int:
    """Count remaining unused backup codes."""
    return BackupCode.objects.filter(user=user, is_used=False).count()
