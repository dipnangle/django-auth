"""Test settings — fast, isolated, no external deps."""

from .base import *  # noqa

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"  # noqa

# ─────────────────────────────────────────────
# Fast password hashing for tests
# ─────────────────────────────────────────────
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# ─────────────────────────────────────────────
# In-memory cache (no Redis needed)
# ─────────────────────────────────────────────
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "session": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "rate_limit": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

# ─────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ─────────────────────────────────────────────
# Celery — synchronous
# ─────────────────────────────────────────────
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ─────────────────────────────────────────────
# Disable rate limiting in tests
# ─────────────────────────────────────────────
RATE_LIMIT["LOGIN_ATTEMPTS"] = 9999  # noqa
RATE_LIMIT["REGISTER_ATTEMPTS"] = 9999  # noqa

# ─────────────────────────────────────────────
# Disable Sentry
# ─────────────────────────────────────────────
import sentry_sdk
sentry_sdk.init(dsn="")
