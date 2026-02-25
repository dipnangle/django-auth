"""SMTP / django-anymail provider."""
from django.core.mail import EmailMultiAlternatives
from apps.notifications.providers.base import BaseEmailProvider
import logging

logger = logging.getLogger(__name__)


class SMTPEmailProvider(BaseEmailProvider):
    def send(self, *, to: str, subject: str, html_body: str, text_body: str = "") -> bool:
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body or "Please view this email in an HTML-capable client.",
                to=[to],
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)
            return True
        except Exception as e:
            logger.error("SMTP send failed to %s: %s", to, e)
            return False
