"""
Account lockout helpers.
Progressive lockout: each lockout doubles the duration.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


def get_lockout_config():
    return {
        "max_attempts": getattr(settings, "ACCOUNT_LOCKOUT", {}).get("MAX_ATTEMPTS", 5),
        "duration_minutes": getattr(settings, "ACCOUNT_LOCKOUT", {}).get("DURATION_MINUTES", 30),
        "progressive": getattr(settings, "ACCOUNT_LOCKOUT", {}).get("PROGRESSIVE", True),
    }


def record_failed_attempt(user) -> dict:
    """
    Record a failed login attempt.
    Returns {"locked": bool, "locked_until": datetime|None, "attempts": int}
    """
    config = get_lockout_config()
    user.failed_login_attempts += 1

    if user.failed_login_attempts >= config["max_attempts"]:
        # Progressive: multiply duration by number of lockouts
        lockout_count = max(1, user.failed_login_attempts // config["max_attempts"])
        if config["progressive"]:
            duration = config["duration_minutes"] * lockout_count
        else:
            duration = config["duration_minutes"]

        user.locked_until = timezone.now() + timedelta(minutes=duration)
        user.save(update_fields=["failed_login_attempts", "locked_until", "updated_at"])

        logger.warning(
            "Account locked: %s | attempts=%d | duration=%dm",
            user.email, user.failed_login_attempts, duration,
        )

        # Send lock notification email async
        try:
            from apps.notifications.services import send_email
            send_email(
                template="account_locked",
                recipient=user.email,
                context={
                    "user": user,
                    "locked_until": user.locked_until,
                    "duration_minutes": duration,
                },
            )
        except Exception:
            pass

        return {"locked": True, "locked_until": user.locked_until, "attempts": user.failed_login_attempts}

    user.save(update_fields=["failed_login_attempts", "updated_at"])
    return {"locked": False, "locked_until": None, "attempts": user.failed_login_attempts}


def check_lockout(user) -> dict:
    """
    Check if account is currently locked.
    Returns {"locked": bool, "locked_until": datetime|None}
    """
    if user.locked_until and user.locked_until > timezone.now():
        return {"locked": True, "locked_until": user.locked_until}

    # Auto-unlock if lockout period expired
    if user.locked_until and user.locked_until <= timezone.now():
        user.locked_until = None
        user.failed_login_attempts = 0
        user.save(update_fields=["locked_until", "failed_login_attempts", "updated_at"])

    return {"locked": False, "locked_until": None}


def reset_failed_attempts(user):
    """Reset failed attempts on successful login."""
    if user.failed_login_attempts > 0 or user.locked_until:
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "locked_until", "updated_at"])
