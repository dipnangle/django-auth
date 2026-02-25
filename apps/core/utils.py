"""
General-purpose utilities used across the platform.
"""

import os
import uuid
import hashlib
import secrets
import logging
import json
from datetime import datetime
from typing import Optional


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Token Generation
# ─────────────────────────────────────────────

def generate_secure_token(length: int = 64) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_short_token(length: int = 8) -> str:
    """Generate a short uppercase token (for invite codes, etc.)."""
    return secrets.token_hex(length // 2).upper()


def generate_numeric_otp(length: int = 6) -> str:
    """Generate a numeric OTP code."""
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])


def hash_token(token: str) -> str:
    """SHA-256 hash of a token. Store the hash, not the raw token."""
    return hashlib.sha256(token.encode()).hexdigest()


# ─────────────────────────────────────────────
# Data Masking (for audit logs / responses)
# ─────────────────────────────────────────────

def mask_email(email: str) -> str:
    """user@example.com → us**@example.com"""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[:2] + "*" * (len(local) - 2)
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """+1234567890 → +12****7890"""
    if len(phone) < 6:
        return "***"
    return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]


def mask_ip(ip: str) -> str:
    """192.168.1.100 → 192.168.1.***"""
    parts = ip.split(".")
    if len(parts) == 4:
        return ".".join(parts[:3]) + ".***"
    return ip  # IPv6 — don't mask for now


# ─────────────────────────────────────────────
# Slug generation
# ─────────────────────────────────────────────

def generate_unique_slug(name: str, model_class, slug_field: str = "slug") -> str:
    """
    Generate a unique slug for a model instance.
    Appends a numeric suffix if the base slug already exists.
    """
    from django.utils.text import slugify
    base_slug = slugify(name)[:50]
    slug = base_slug
    counter = 1
    while model_class.all_objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


# ─────────────────────────────────────────────
# JSON Logging Formatter
# ─────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """
    Outputs log records as JSON for log aggregation tools (Datadog, ELK, etc.)
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (request_id, user_id, etc.)
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
            }:
                try:
                    json.dumps(value)  # Check if serializable
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)

        return json.dumps(log_data)


# ─────────────────────────────────────────────
# Misc Helpers
# ─────────────────────────────────────────────

def get_client_ip(request) -> str:
    """Extract real client IP from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split a list into chunks of given size. Useful for bulk DB ops."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(dictionary: dict, *keys, default=None):
    """Safely get a nested key from a dict without KeyError."""
    current = dictionary
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def str_to_bool(value: str) -> bool:
    """Convert string 'true'/'false'/'1'/'0' to bool."""
    return str(value).lower() in ("true", "1", "yes", "on")


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filenames."""
    import re
    filename = re.sub(r"[^\w\s\-\.]", "", filename)
    return filename[:255]
