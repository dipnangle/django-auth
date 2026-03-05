"""
Authentication service layer.
All auth flows (login, logout, register, reset) live here.
"""

import logging
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from apps.core.exceptions import (
    AuthenticationFailed, AccountLocked, AccountSuspended,
    AccountNotVerified, TwoFactorRequired, ResourceNotFound,
    ValidationError, TokenInvalid,
)
from apps.core.utils import generate_secure_token, hash_token

logger = logging.getLogger(__name__)


@transaction.atomic
def login_user(*, email: str, password: str, ip_address: str = "", user_agent: str = "") -> dict:
    """
    Full login flow:
    1. Rate limit check
    2. User lookup
    3. Account status checks (locked, suspended, active)
    4. Password verification
    5. 2FA check (if enabled/enforced)
    6. Token generation
    7. Session creation
    """
    from apps.authentication.rate_limit import get_login_limiter

    # 1. Rate limit by IP and email
    ip_limiter = get_login_limiter(ip_address)
    email_limiter = get_login_limiter(email.lower())
    ip_limiter.check()
    email_limiter.check()

    # 2. User lookup (use all_including_deleted to detect deleted accounts)
    from apps.users.models import User
    try:
        user = User.objects.select_related("global_role").get(email__iexact=email)
    except User.DoesNotExist:
        # Increment rate limit to prevent enumeration timing attacks
        ip_limiter.increment()
        email_limiter.increment()
        raise AuthenticationFailed("Invalid email or password.")

    # 3. Account status checks
    if user.is_deleted:
        raise AuthenticationFailed("Invalid email or password.")

    if user.is_suspended:
        raise AccountSuspended()

    if user.is_locked:
        raise AccountLocked(
            f"Your account is locked until {user.locked_until.strftime('%Y-%m-%d %H:%M UTC')}."
        )

    if not user.is_active:
        raise AuthenticationFailed("This account is inactive.")

    # 4. Password check
    if not user.check_password(password):
        ip_limiter.increment()
        email_limiter.increment()
        user.record_failed_login()
        raise AuthenticationFailed("Invalid email or password.")

    # 5. Email verification
    if not user.is_email_verified:
        raise AccountNotVerified()

    # 6. 2FA check
    if user.is_2fa_enabled or user.is_2fa_enforced:
        partial_token = _generate_partial_auth_token(user)
        method = getattr(user, "two_fa_method", "totp")

        # Auto-send OTP if user uses email method
        if method == "email":
            try:
                from apps.two_factor.services import send_email_otp
                send_email_otp(user=user, ip_address=ip_address)
            except Exception as e:
                logger.error("Failed to send email OTP: %s", e)

        return {
            "requires_2fa": True,
            "method": method,
            "partial_token": partial_token,
            "message": "2FA verification required. Check your email." if method == "email" else "2FA verification required.",
        }

    # 7. Full auth — generate tokens
    from apps.authentication.tokens import generate_token_pair
    tokens = generate_token_pair(user)

    # 8. Record login + create session
    user.record_login(ip_address=ip_address)
    from apps.sessions.services import create_session
    create_session(
        user=user,
        jti=tokens["refresh_jti"],
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # 9. Reset rate limiters on success
    ip_limiter.reset()
    email_limiter.reset()

    logger.info("User logged in: %s from %s", user.email, ip_address)
    return {
        "requires_2fa": False,
        **tokens,
        "user_id": str(user.id),
        "email": user.email,
    }


def _generate_partial_auth_token(user) -> str:
    """
    Short-lived token issued after password check but before 2FA.
    Used to identify the user during 2FA verification step.
    """
    from apps.authentication.tokens import generate_access_token
    # Reuse access token with a shorter life and a 2fa_pending flag
    import jwt
    from datetime import datetime, timezone as dt_timezone
    from django.conf import settings as s
    import uuid

    now = datetime.now(dt_timezone.utc)
    payload = {
        "token_type": "2fa_pending",
        "user_id": str(user.id),
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "iss": s.JWT_SETTINGS["ISSUER"],
        "aud": s.JWT_SETTINGS["AUDIENCE"],
    }
    return jwt.encode(payload, s.JWT_SETTINGS["SIGNING_KEY"], algorithm=s.JWT_SETTINGS["ALGORITHM"])


def logout_user(*, user, refresh_token: str = None, jti: str = None) -> None:
    """
    Logout: blacklist the refresh token and revoke session.
    """
    from apps.authentication.tokens import blacklist_token, decode_refresh_token
    from apps.sessions.services import revoke_session_by_jti

    if refresh_token:
        try:
            payload = decode_refresh_token(refresh_token)
            jti = payload.get("jti")
        except Exception:
            pass

    if jti:
        blacklist_token(jti)
        revoke_session_by_jti(jti=jti)

    logger.info("User logged out: %s", user.email)


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    ip_address: str = "",
) -> "User":
    """
    Self-registration for END_USER role.
    """
    from apps.authentication.rate_limit import get_register_limiter
    from apps.roles.selectors import get_role_by_name
    from apps.users.services import create_user

    # Rate limit registration by IP
    limiter = get_register_limiter(ip_address)
    limiter.check_and_increment()

    role = get_role_by_name("END_USER")

    user = create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        send_verification=True,
        is_email_verified=False,
    )

    return user


@transaction.atomic
def send_verification_email(*, user) -> None:
    """Send or resend email verification link."""
    from apps.authentication.models import EmailVerificationToken
    from apps.notifications.services import send_email

    # Delete existing token
    EmailVerificationToken.objects.filter(user=user).delete()

    raw_token = generate_secure_token(48)
    token_hash = hash_token(raw_token)
    expires_at = timezone.now() + timedelta(hours=24)

    EmailVerificationToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    frontend_url = settings.PLATFORM["FRONTEND_URL"]
    verify_url = f"{frontend_url}/verify-email?token={raw_token}"

    send_email(
        to=user.email,
        template="email_verify",
        context={"user": user, "verification_url": verify_url, "expires_hours": 24},
    )


@transaction.atomic
def verify_email(*, token: str) -> "User":
    """Verify a user's email address using the token from the email link."""
    from apps.authentication.models import EmailVerificationToken

    token_hash = hash_token(token)
    try:
        record = EmailVerificationToken.objects.select_related("user").get(
            token_hash=token_hash,
            is_used=False,
        )
    except EmailVerificationToken.DoesNotExist:
        raise TokenInvalid("Invalid or expired verification link.")

    if record.is_expired:
        raise TokenInvalid("This verification link has expired. Please request a new one.")

    record.is_used = True
    record.used_at = timezone.now()
    record.save(update_fields=["is_used", "used_at"])

    user = record.user
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified", "updated_at"])

    logger.info("Email verified: %s", user.email)
    return user


@transaction.atomic
def request_password_reset(*, email: str, ip_address: str = "") -> None:
    """Send password reset email."""
    from apps.authentication.models import PasswordResetToken
    from apps.authentication.rate_limit import get_password_reset_limiter
    from apps.notifications.services import send_email
    from apps.users.selectors import get_user_by_email_or_none

    limiter = get_password_reset_limiter(email.lower())
    limiter.check_and_increment()

    user = get_user_by_email_or_none(email)

    # Always return success to prevent email enumeration
    if not user or not user.is_active or user.is_deleted:
        return

    raw_token = generate_secure_token(48)
    token_hash = hash_token(raw_token)
    expires_at = timezone.now() + timedelta(hours=1)

    # Invalidate old tokens
    PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

    PasswordResetToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at,
        requested_ip=ip_address,
    )

    frontend_url = settings.PLATFORM["FRONTEND_URL"]
    reset_url = f"{frontend_url}/reset-password?token={raw_token}"

    send_email(
        to=user.email,
        template="password_reset",
        context={"user": user, "reset_url": reset_url, "expires_minutes": 60},
    )


@transaction.atomic
def confirm_password_reset(*, token: str, new_password: str) -> "User":
    """Complete password reset using token from email."""
    from apps.authentication.models import PasswordResetToken
    from django.contrib.auth.password_validation import validate_password

    token_hash = hash_token(token)
    try:
        record = PasswordResetToken.objects.select_related("user").get(
            token_hash=token_hash,
            is_used=False,
        )
    except PasswordResetToken.DoesNotExist:
        raise TokenInvalid("Invalid or expired password reset link.")

    if record.is_expired:
        raise TokenInvalid("This reset link has expired. Please request a new one.")

    user = record.user
    validate_password(new_password, user)

    user.set_password(new_password)
    user.password_changed_at = timezone.now()
    user.must_change_password = False
    user.failed_login_attempts = 0
    user.locked_until = None
    user.save(update_fields=[
        "password", "password_changed_at", "must_change_password",
        "failed_login_attempts", "locked_until", "updated_at",
    ])

    record.is_used = True
    record.used_at = timezone.now()
    record.save(update_fields=["is_used", "used_at"])

    # Revoke all sessions (force re-login everywhere)
    from apps.sessions.services import revoke_all_sessions
    revoke_all_sessions(user=user)

    logger.info("Password reset completed: %s", user.email)
    return user
