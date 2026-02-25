"""Two-factor authentication services."""

import logging
import pyotp
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from apps.core.exceptions import TwoFactorInvalid, ValidationError
from apps.core.utils import generate_secure_token, hash_token

logger = logging.getLogger(__name__)

TWO_FACTOR = settings.TWO_FACTOR


@transaction.atomic
def setup_totp(*, user) -> dict:
    """
    Initialize TOTP setup for a user.
    Returns the secret and provisioning URI for QR code generation.
    Call confirm_totp() after user verifies the first code.
    """
    from apps.two_factor.models import TOTPDevice

    # Delete existing unconfirmed device
    TOTPDevice.objects.filter(user=user, is_confirmed=False).delete()

    secret = pyotp.random_base32()
    TOTPDevice.objects.create(user=user, secret=secret, is_confirmed=False)

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name=TWO_FACTOR["TOTP_ISSUER"],
    )

    # Generate QR code as base64
    qr_base64 = _generate_qr_base64(provisioning_uri)

    return {
        "secret": secret,
        "provisioning_uri": provisioning_uri,
        "qr_code_base64": qr_base64,
    }


@transaction.atomic
def confirm_totp(*, user, code: str) -> dict:
    """
    Confirm TOTP setup by verifying the first code.
    On success: enables 2FA and generates backup codes.
    """
    from apps.two_factor.models import TOTPDevice

    try:
        device = TOTPDevice.objects.get(user=user, is_confirmed=False)
    except TOTPDevice.DoesNotExist:
        raise ValidationError("No pending 2FA setup found. Please start setup again.")

    totp = pyotp.TOTP(device.secret)
    if not totp.verify(code, valid_window=TWO_FACTOR["TOTP_VALID_WINDOW"]):
        raise TwoFactorInvalid("Invalid verification code.")

    device.is_confirmed = True
    device.confirmed_at = timezone.now()
    device.save(update_fields=["is_confirmed", "confirmed_at"])

    user.is_2fa_enabled = True
    user.save(update_fields=["is_2fa_enabled", "updated_at"])

    backup_codes = generate_backup_codes(user=user)
    logger.info("2FA enabled for user: %s", user.email)

    return {"backup_codes": backup_codes, "message": "2FA enabled successfully."}


def verify_totp(*, user, code: str) -> bool:
    """
    Verify a TOTP code during login.
    Also accepts backup codes.
    """
    from apps.two_factor.models import TOTPDevice
    from apps.authentication.rate_limit import get_2fa_limiter

    limiter = get_2fa_limiter(str(user.id))
    limiter.check()

    # Try TOTP first
    try:
        device = TOTPDevice.objects.get(user=user, is_confirmed=True)
        totp = pyotp.TOTP(device.secret)
        if totp.verify(code, valid_window=TWO_FACTOR["TOTP_VALID_WINDOW"]):
            device.last_used_at = timezone.now()
            device.save(update_fields=["last_used_at"])
            limiter.reset()
            return True
    except TOTPDevice.DoesNotExist:
        pass

    # Try backup code
    if _verify_backup_code(user=user, code=code):
        limiter.reset()
        return True

    limiter.increment()
    raise TwoFactorInvalid("Invalid 2FA code.")


def _verify_backup_code(*, user, code: str) -> bool:
    """Check and consume a backup code."""
    from apps.two_factor.models import BackupCode

    code_hash = hash_token(code.strip().upper())
    try:
        backup = BackupCode.objects.get(user=user, code_hash=code_hash, is_used=False)
        backup.is_used = True
        backup.used_at = timezone.now()
        backup.save(update_fields=["is_used", "used_at"])
        return True
    except BackupCode.DoesNotExist:
        return False


@transaction.atomic
def generate_backup_codes(*, user) -> list[str]:
    """
    Generate fresh backup codes. Replaces all existing unused codes.
    Returns the raw codes (only shown once — store the hashes).
    """
    from apps.two_factor.models import BackupCode

    BackupCode.objects.filter(user=user, is_used=False).delete()

    count = TWO_FACTOR["BACKUP_CODES_COUNT"]
    length = TWO_FACTOR["BACKUP_CODE_LENGTH"]
    raw_codes = []

    for _ in range(count):
        raw = generate_secure_token(length // 2).upper()[:length]
        raw_codes.append(raw)
        BackupCode.objects.create(user=user, code_hash=hash_token(raw))

    return raw_codes


@transaction.atomic
def disable_totp(*, user, confirmed_by=None) -> None:
    """Disable 2FA for a user. Only ROOT can disable for other users."""
    from apps.two_factor.models import TOTPDevice, BackupCode

    TOTPDevice.objects.filter(user=user).delete()
    BackupCode.objects.filter(user=user, is_used=False).delete()

    user.is_2fa_enabled = False
    user.save(update_fields=["is_2fa_enabled", "updated_at"])
    logger.info("2FA disabled for user: %s (by: %s)", user.email, confirmed_by)


def complete_2fa_login(*, user, ip_address: str = "", user_agent: str = "") -> dict:
    """
    Called after successful 2FA verification.
    Issues full token pair and creates session.
    """
    from apps.authentication.tokens import generate_token_pair
    from apps.sessions.services import create_session

    tokens = generate_token_pair(user)
    user.record_login(ip_address=ip_address)

    create_session(
        user=user,
        jti=tokens["refresh_jti"],
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return {
        "requires_2fa": False,
        **tokens,
        "user_id": str(user.id),
        "email": user.email,
    }


def _generate_qr_base64(provisioning_uri: str) -> str:
    """Generate base64-encoded QR code PNG."""
    try:
        import qrcode
        import io
        import base64

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except ImportError:
        return ""
