"""
Staging settings — mirrors production but with relaxed monitoring.
Use DJANGO_ENV=staging on your test server.
"""

from .production import *  # noqa
from decouple import config

# ─────────────────────────────────────────────
# Override for staging
# ─────────────────────────────────────────────
DEBUG = False

# Staging-specific allowed hosts
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="", cast=lambda v: [s.strip() for s in v.split(",")])

# ─────────────────────────────────────────────
# Relaxed rate limits for staging testing
# ─────────────────────────────────────────────
RATE_LIMIT["LOGIN_ATTEMPTS"] = 20        # noqa
RATE_LIMIT["REGISTER_ATTEMPTS"] = 50     # noqa

# ─────────────────────────────────────────────
# Email — use console in staging unless configured
# ─────────────────────────────────────────────
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# ─────────────────────────────────────────────
# Sentry — separate staging environment
# ─────────────────────────────────────────────
import sentry_sdk
sentry_sdk.init(
    dsn=config("SENTRY_DSN", default=""),
    environment="staging",
    traces_sample_rate=1.0,  # Full traces in staging
)

# ─────────────────────────────────────────────
# Looser CORS for staging frontend testing
# ─────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = config("STAGING_CORS_ALLOW_ALL", default=False, cast=bool)
