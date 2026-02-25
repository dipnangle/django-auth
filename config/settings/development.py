"""Development settings — local development only."""

from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ─────────────────────────────────────────────
# Dev-only apps
# ─────────────────────────────────────────────
INSTALLED_APPS += [  # noqa
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE += [  # noqa
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]

# ─────────────────────────────────────────────
# Database (local)
# ─────────────────────────────────────────────
DATABASES["default"]["NAME"] = "platform_dev"  # noqa

# ─────────────────────────────────────────────
# Email — print to console
# ─────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─────────────────────────────────────────────
# CORS — allow all in dev
# ─────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ─────────────────────────────────────────────
# Celery — run tasks eagerly in dev (no broker needed)
# ─────────────────────────────────────────────
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ─────────────────────────────────────────────
# Django Debug Toolbar
# ─────────────────────────────────────────────
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

# ─────────────────────────────────────────────
# Looser rate limits for development
# ─────────────────────────────────────────────
RATE_LIMIT["LOGIN_ATTEMPTS"] = 100  # noqa
RATE_LIMIT["REGISTER_ATTEMPTS"] = 100  # noqa
