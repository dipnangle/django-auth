"""System config services."""

import logging
from django.core.cache import cache
from apps.system_config.models import SystemConfig
from apps.system_config.defaults import DEFAULTS

logger = logging.getLogger(__name__)


def set_config(key: str, value, updated_by=None) -> SystemConfig:
    """Set a system config value. Creates if not exists."""
    config, _ = SystemConfig.objects.update_or_create(
        key=key,
        defaults={
            "value": value,
            "updated_by": updated_by,
            "description": DEFAULTS.get(key, {}).get("description", "") if isinstance(DEFAULTS.get(key), dict) else "",
        },
    )
    # Invalidate cache
    cache.delete(f"system_config:{key}")
    logger.info("System config updated: %s = %s (by %s)", key, value, updated_by)
    return config


def seed_defaults(updated_by=None):
    """
    Seed all default system config values into DB.
    Does NOT overwrite existing values — safe to run multiple times.
    Called by management command: python manage.py seed_system_config
    """
    created_count = 0
    for key, value in DEFAULTS.items():
        _, created = SystemConfig.objects.get_or_create(
            key=key,
            defaults={"value": value, "updated_by": updated_by},
        )
        if created:
            created_count += 1
            logger.info("Seeded system config: %s = %s", key, value)

    logger.info("System config seeded: %d new entries", created_count)
    return created_count
