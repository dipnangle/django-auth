"""
Notification service — email abstraction.
All emails go through this. Never call Django's send_mail directly.
"""

import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_email(*, to: str, template: str, context: dict, subject: str = None) -> bool:
    """
    Send a templated email.
    In production this queues via Celery.
    In dev/test it sends synchronously.
    """
    try:
        from apps.notifications.tasks import send_email_task
        send_email_task.delay(to=to, template=template, context=_serialize_context(context), subject=subject)
        return True
    except Exception as e:
        logger.warning("Failed to queue email, sending synchronously: %s", str(e))
        return _send_email_sync(to=to, template=template, context=context, subject=subject)


def _send_email_sync(*, to: str, template: str, context: dict, subject: str = None) -> bool:
    """Synchronous email sending — used in dev/test or as fallback."""
    try:
        platform_name = settings.PLATFORM["NAME"]
        from_email = settings.DEFAULT_FROM_EMAIL

        # Add common context
        context.setdefault("platform_name", platform_name)
        context.setdefault("frontend_url", settings.PLATFORM["FRONTEND_URL"])
        context.setdefault("support_email", settings.PLATFORM["SUPPORT_EMAIL"])

        # Render templates
        html_content = render_to_string(f"{template}.html", context)
        text_content = render_to_string(f"{template}.txt", context) if _template_exists(f"{template}.txt") else _strip_html(html_content)

        if not subject:
            subject = _get_default_subject(template, platform_name)

        msg = EmailMultiAlternatives(
            subject=f"{settings.EMAIL_SUBJECT_PREFIX}{subject}",
            body=text_content,
            from_email=from_email,
            to=[to],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Email sent: %s → %s", template, to)
        return True
    except Exception as e:
        logger.error("Failed to send email '%s' to '%s': %s", template, to, str(e))
        return False


def _get_default_subject(template: str, platform_name: str) -> str:
    subjects = {
        "email_verify": f"Verify your email — {platform_name}",
        "password_reset": f"Reset your password — {platform_name}",
        "invitation": f"You've been invited to join {platform_name}",
        "login_alert": f"New login detected — {platform_name}",
        "account_locked": f"Your account has been locked — {platform_name}",
    }
    return subjects.get(template, f"Notification from {platform_name}")


def _template_exists(template_name: str) -> bool:
    from django.template.loader import get_template
    try:
        get_template(template_name)
        return True
    except Exception:
        return False


def _strip_html(html: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", html).strip()


def _serialize_context(context: dict) -> dict:
    """Make context JSON-serializable for Celery task queuing."""
    result = {}
    for key, value in context.items():
        if hasattr(value, "id"):
            result[f"{key}_id"] = str(value.id)
            result[f"{key}_str"] = str(value)
        elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
            result[key] = value
        else:
            result[key] = str(value)
    return result
