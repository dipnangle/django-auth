"""
Base settings shared across all environments.
Environment-specific settings override these in development.py / production.py
"""

import os
from pathlib import Path
from decouple import config, Csv

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

# ─────────────────────────────────────────────
# Security
# ─────────────────────────────────────────────
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="", cast=Csv())

# Deployment mode: 'saas' or 'self_hosted'
DEPLOYMENT_MODE = config("DEPLOYMENT_MODE", default="saas")

# ─────────────────────────────────────────────
# Application definition
# ─────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
    "django_celery_results",
    "django_prometheus",
]

LOCAL_APPS = [
    "apps.core",
    "apps.users",
    "apps.roles",
    "apps.organizations",
    "apps.plans",
    "apps.permissions",
    "apps.authentication",
    "apps.two_factor",
    "apps.sessions",
    "apps.invitations",
    "apps.audit",
    "apps.impersonation",
    "apps.system_config",
    "apps.notifications",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom
    "apps.core.middleware.RequestIDMiddleware",
    "apps.core.middleware.AuditContextMiddleware",
    "apps.core.middleware.TenantMiddleware",
    "apps.sessions.middleware.SessionTrackingMiddleware",
    "apps.impersonation.middleware.ImpersonationMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ─────────────────────────────────────────────
# Templates
# ─────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ─────────────────────────────────────────────
# Database — PostgreSQL
# ─────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="platform_db"),
        "USER": config("DB_USER", default="platform_user"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
    }
}

# Read replica (optional, used by selectors for heavy reads)
if config("DB_REPLICA_HOST", default=""):
    DATABASES["replica"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="platform_db"),
        "USER": config("DB_USER", default="platform_user"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_REPLICA_HOST"),
        "PORT": config("DB_REPLICA_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
        "TEST": {"MIRROR": "default"},
    }

# ─────────────────────────────────────────────
# Redis
# ─────────────────────────────────────────────
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/0",
        "OPTIONS": {
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "platform",
        "TIMEOUT": 300,
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "KEY_PREFIX": "session",
        "TIMEOUT": 86400,
    },
    "rate_limit": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/2",
        "KEY_PREFIX": "rl",
        "TIMEOUT": 3600,
    },
}

# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "apps.authentication.backends.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "apps.core.validators.PasswordComplexityValidator"},
]

# ─────────────────────────────────────────────
# JWT Settings
# ─────────────────────────────────────────────
JWT_SETTINGS = {
    "ACCESS_TOKEN_LIFETIME_MINUTES": config("JWT_ACCESS_MINUTES", default=15, cast=int),
    "REFRESH_TOKEN_LIFETIME_DAYS": config("JWT_REFRESH_DAYS", default=7, cast=int),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("JWT_SIGNING_KEY", default=config("DJANGO_SECRET_KEY")),
    "ISSUER": config("JWT_ISSUER", default="platform"),
    "AUDIENCE": config("JWT_AUDIENCE", default="platform-api"),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ─────────────────────────────────────────────
# DRF
# ─────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.authentication.backends.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "300/minute",
        "auth": "10/minute",
    },
}

# ─────────────────────────────────────────────
# API Docs (drf-spectacular)
# ─────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Platform API",
    "DESCRIPTION": "Multi-tenant SaaS platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
}

# ─────────────────────────────────────────────
# Celery
# ─────────────────────────────────────────────
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=f"{REDIS_URL}/3")
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 min hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ─────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@platform.com")
EMAIL_SUBJECT_PREFIX = config("EMAIL_SUBJECT_PREFIX", default="[Platform] ")

# ─────────────────────────────────────────────
# Static & Media
# ─────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─────────────────────────────────────────────
# Internationalization
# ─────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# Default primary key
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# ─────────────────────────────────────────────
# Rate Limiting (custom settings, used by apps.authentication.rate_limit)
# ─────────────────────────────────────────────
RATE_LIMIT = {
    "LOGIN_ATTEMPTS": config("RL_LOGIN_ATTEMPTS", default=5, cast=int),
    "LOGIN_WINDOW_SECONDS": config("RL_LOGIN_WINDOW", default=300, cast=int),
    "REGISTER_ATTEMPTS": config("RL_REGISTER_ATTEMPTS", default=10, cast=int),
    "REGISTER_WINDOW_SECONDS": config("RL_REGISTER_WINDOW", default=3600, cast=int),
    "PASSWORD_RESET_ATTEMPTS": config("RL_PW_RESET_ATTEMPTS", default=3, cast=int),
    "PASSWORD_RESET_WINDOW_SECONDS": config("RL_PW_RESET_WINDOW", default=3600, cast=int),
}

# ─────────────────────────────────────────────
# Account Lockout (overridable via system_config in DB)
# ─────────────────────────────────────────────
ACCOUNT_LOCKOUT = {
    "MAX_FAILED_ATTEMPTS": config("LOCKOUT_MAX_ATTEMPTS", default=5, cast=int),
    "LOCKOUT_DURATION_MINUTES": config("LOCKOUT_DURATION_MINUTES", default=30, cast=int),
    "PROGRESSIVE_LOCKOUT": True,  # Each lockout doubles duration
}

# ─────────────────────────────────────────────
# 2FA Settings
# ─────────────────────────────────────────────
TWO_FACTOR = {
    "TOTP_ISSUER": config("TOTP_ISSUER", default="Platform"),
    "BACKUP_CODES_COUNT": 8,
    "BACKUP_CODE_LENGTH": 12,
    "TOTP_VALID_WINDOW": 1,  # Allow 1 step drift
}

# ─────────────────────────────────────────────
# Invitation Settings
# ─────────────────────────────────────────────
INVITATION = {
    "TOKEN_EXPIRY_HOURS": config("INVITE_TOKEN_EXPIRY_HOURS", default=72, cast=int),
    "MAX_PENDING_PER_ORG": config("INVITE_MAX_PENDING", default=100, cast=int),
}

# ─────────────────────────────────────────────
# Audit Log Retention (default, overridden by plan)
# ─────────────────────────────────────────────
AUDIT = {
    "DEFAULT_RETENTION_DAYS": 30,
    "CLEANUP_BATCH_SIZE": 1000,
}

# ─────────────────────────────────────────────
# Platform Info
# ─────────────────────────────────────────────
PLATFORM = {
    "NAME": config("PLATFORM_NAME", default="Platform"),
    "FRONTEND_URL": config("FRONTEND_URL", default="http://localhost:3000"),
    "SUPPORT_EMAIL": config("SUPPORT_EMAIL", default="support@platform.com"),
    "VERSION": "1.0.0",
}

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "()": "apps.core.utils.JSONFormatter",
        },
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# ─────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=465, cast=int)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=True, cast=bool)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@yourplatform.com")
EMAIL_SUBJECT_PREFIX = config("EMAIL_SUBJECT_PREFIX", default="")
