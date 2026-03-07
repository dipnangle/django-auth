"""Production settings — strict, secure, optimized."""

from .base import *  # noqa

DEBUG = False

# ─────────────────────────────────────────────
# Security
# ─────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ─────────────────────────────────────────────
# Database — Connection pooling via PgBouncer
# ─────────────────────────────────────────────
DATABASES["default"]["CONN_MAX_AGE"] = 60  # noqa

# ─────────────────────────────────────────────
# Static files (WhiteNoise)
# ─────────────────────────────────────────────
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ─────────────────────────────────────────────
# Email — SMTP (configured via .env)
# ─────────────────────────────────────────────
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")

# ─────────────────────────────────────────────
# Sentry
# ─────────────────────────────────────────────
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

sentry_sdk.init(
    dsn=config("SENTRY_DSN", default=""),  # noqa
    integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment="production",
)

# ─────────────────────────────────────────────
# Storage (S3 for media)
# ─────────────────────────────────────────────
if config("USE_S3", default=False, cast=bool):  # noqa
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")  # noqa
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")  # noqa
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")  # noqa
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")  # noqa
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

# ─────────────────────────────────────────────
# Logging — JSON to stdout (for log aggregators)
# ─────────────────────────────────────────────
LOGGING["handlers"]["console"]["formatter"] = "json"  # noqa
