"""System config selectors."""

import json
from django.core.cache import cache
from apps.system_config.models import SystemConfig
from apps.system_config.defaults import DEFAULTS

CACHE_TTL = 300  # 5 minutes


def get_config(key: str, default=None):
    """
    Get a system config value by key.
    Checks cache first, then DB, then defaults.
    """
    cache_key = f"system_config:{key}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        config = SystemConfig.objects.get(key=key)
        value = config.value
    except SystemConfig.DoesNotExist:
        value = DEFAULTS.get(key, default)

    if value is not None:
        cache.set(cache_key, value, CACHE_TTL)

    return value


def get_all_configs() -> dict:
    """Get all system configs as a dictionary."""
    configs = {}
    for item in SystemConfig.objects.all():
        configs[item.key] = item.value
    # Fill in defaults for anything not in DB
    for key, value in DEFAULTS.items():
        if key not in configs:
            configs[key] = value
    return configs


def is_maintenance_mode() -> bool:
    return bool(get_config("maintenance_mode", False))


def get_lockout_max_attempts() -> int:
    return int(get_config("lockout_max_attempts", 5))


def get_lockout_duration_minutes() -> int:
    return int(get_config("lockout_duration_minutes", 30))


def get_password_min_length() -> int:
    return int(get_config("password_min_length", 10))


def get_session_max_per_user() -> int:
    return int(get_config("session_max_per_user", 10))


def is_self_registration_allowed() -> bool:
    return bool(get_config("allow_self_registration", True))
