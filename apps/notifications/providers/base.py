"""Base email provider interface."""
from abc import ABC, abstractmethod


class BaseEmailProvider(ABC):
    @abstractmethod
    def send(self, *, to: str, subject: str, html_body: str, text_body: str = "") -> bool:
        """Send an email. Returns True on success."""
        ...
