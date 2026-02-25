"""Session services."""

import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


def create_session(*, user, jti: str, ip_address: str = "", user_agent: str = "") -> "UserSession":
    from apps.sessions.models import UserSession

    expires_at = timezone.now() + timedelta(days=settings.JWT_SETTINGS["REFRESH_TOKEN_LIFETIME_DAYS"])
    device_type, browser, os_ = _parse_user_agent(user_agent)

    return UserSession.objects.create(
        user=user,
        jti=jti,
        ip_address=ip_address or None,
        user_agent=user_agent[:512],
        device_type=device_type,
        browser=browser,
        os=os_,
        expires_at=expires_at,
        is_active=True,
    )


def revoke_session_by_jti(*, jti: str) -> None:
    from apps.sessions.models import UserSession
    UserSession.objects.filter(jti=jti, is_active=True).update(
        is_active=False,
        revoked_at=timezone.now(),
        revoked_reason="logout",
    )


def revoke_session_by_id(*, session_id: str, revoked_by) -> None:
    from apps.sessions.models import UserSession
    from apps.core.exceptions import ResourceNotFound, PermissionDeniedException

    try:
        session = UserSession.objects.get(id=session_id)
    except UserSession.DoesNotExist:
        raise ResourceNotFound("Session not found.")

    if str(session.user_id) != str(revoked_by.id) and not revoked_by.is_root:
        raise PermissionDeniedException("You can only revoke your own sessions.")

    session.is_active = False
    session.revoked_at = timezone.now()
    session.revoked_reason = "manual"
    session.save(update_fields=["is_active", "revoked_at", "revoked_reason"])

    from apps.authentication.tokens import blacklist_token
    blacklist_token(session.jti)


def revoke_all_sessions(*, user, except_jti: str = None) -> int:
    """Revoke all active sessions for a user. Returns count revoked."""
    from apps.sessions.models import UserSession
    from apps.authentication.tokens import blacklist_all_user_tokens

    qs = UserSession.objects.filter(user=user, is_active=True)
    if except_jti:
        qs = qs.exclude(jti=except_jti)

    count = qs.update(
        is_active=False,
        revoked_at=timezone.now(),
        revoked_reason="force_logout",
    )

    blacklist_all_user_tokens(str(user.id))
    logger.info("Revoked %d sessions for user: %s", count, user.email)
    return count


def list_active_sessions(*, user):
    from apps.sessions.models import UserSession
    return UserSession.objects.filter(user=user, is_active=True, expires_at__gt=timezone.now())


def cleanup_expired_sessions() -> int:
    """Celery task: remove expired sessions from DB. Run daily."""
    from apps.sessions.models import UserSession
    deleted, _ = UserSession.objects.filter(
        is_active=False,
        revoked_at__lt=timezone.now() - timedelta(days=90),
    ).delete()
    return deleted


def _parse_user_agent(user_agent: str) -> tuple[str, str, str]:
    """Basic UA parsing. Extend with user-agents library for production."""
    ua = user_agent.lower()
    device = "desktop"
    if "mobile" in ua:
        device = "mobile"
    elif "tablet" in ua or "ipad" in ua:
        device = "tablet"

    browser = "unknown"
    for b in ["chrome", "firefox", "safari", "edge", "opera"]:
        if b in ua:
            browser = b.capitalize()
            break

    os_ = "unknown"
    for o, label in [("windows", "Windows"), ("mac", "macOS"), ("linux", "Linux"),
                     ("android", "Android"), ("ios", "iOS"), ("iphone", "iOS")]:
        if o in ua:
            os_ = label
            break

    return device, browser, os_
