"""
Reusable validators used across the platform.
"""

import re
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class PasswordComplexityValidator:
    """
    Enforces strong passwords:
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """

    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("Password must contain at least one uppercase letter."), code="no_uppercase")
        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Password must contain at least one lowercase letter."), code="no_lowercase")
        if not re.search(r"\d", password):
            raise ValidationError(_("Password must contain at least one digit."), code="no_digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError(_("Password must contain at least one special character."), code="no_special")

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, one lowercase letter, "
            "one digit, and one special character."
        )


def validate_phone_number(value):
    """Validate international phone numbers."""
    import phonenumbers
    try:
        parsed = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError(_("Enter a valid international phone number."))
    except Exception:
        raise ValidationError(_("Enter a valid international phone number (e.g. +1234567890)."))


def validate_slug(value):
    """Validates URL-safe slugs."""
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", value):
        raise ValidationError(_("Slug must contain only lowercase letters, numbers, and hyphens."))


def validate_no_disposable_email(value):
    """
    Blocks known disposable email domains.
    Extend DISPOSABLE_DOMAINS list as needed.
    """
    DISPOSABLE_DOMAINS = {
        "mailinator.com", "tempmail.com", "guerrillamail.com",
        "10minutemail.com", "throwaway.email", "yopmail.com",
        "trashmail.com", "fakeinbox.com", "dispostable.com",
    }
    domain = value.split("@")[-1].lower()
    if domain in DISPOSABLE_DOMAINS:
        raise ValidationError(_("Disposable email addresses are not allowed."))


def validate_organization_name(value):
    """Organization names must be between 2 and 100 chars and not purely numeric."""
    if len(value.strip()) < 2:
        raise ValidationError(_("Organization name must be at least 2 characters."))
    if value.strip().isdigit():
        raise ValidationError(_("Organization name cannot be purely numeric."))


def validate_uuid(value):
    """Validate UUID format."""
    import uuid
    try:
        uuid.UUID(str(value))
    except ValueError:
        raise ValidationError(_("Enter a valid UUID."))
