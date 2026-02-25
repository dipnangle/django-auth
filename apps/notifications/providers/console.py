"""Console email provider — prints to stdout (dev/test)."""
from apps.notifications.providers.base import BaseEmailProvider
import logging

logger = logging.getLogger(__name__)


class ConsoleEmailProvider(BaseEmailProvider):
    def send(self, *, to: str, subject: str, html_body: str, text_body: str = "") -> bool:
        logger.info("=" * 60)
        logger.info("[EMAIL] To: %s", to)
        logger.info("[EMAIL] Subject: %s", subject)
        logger.info("[EMAIL] Body preview: %s", (text_body or html_body)[:200])
        logger.info("=" * 60)
        return True
