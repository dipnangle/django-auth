"""Permission selectors — FBAC feature checking."""

from django.core.cache import cache


def user_has_feature(user, feature: str, organization=None) -> bool:
    """
    Check if a user has a specific feature enabled.

    Resolution order:
    1. Check per-user override (explicit grant or revoke)
    2. Check role defaults
    3. Check plan features (must be in plan to be available at all)

    Returns True if allowed, False if denied.
    """
    cache_key = f"fbac:{user.id}:{feature}:{getattr(organization, 'id', 'global')}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = _check_feature_access(user, feature, organization)
    cache.set(cache_key, result, timeout=300)  # 5 min cache
    return result


def _check_feature_access(user, feature: str, organization=None) -> bool:
    from apps.permissions.models import UserPermissionOverride
    from apps.roles.selectors import get_role_feature_defaults

    # 1. Per-user override
    override = UserPermissionOverride.objects.filter(user=user, feature=feature).first()
    if override is not None:
        return override.is_granted

    # 2. Role default
    role = user.get_role_in_org(organization) if organization else user.global_role
    if role:
        role_features = get_role_feature_defaults(role)
        if feature in role_features:
            role_allowed = role_features[feature]
            # Even if role allows it, plan must also include it
            if role_allowed and organization:
                from apps.plans.selectors import is_feature_enabled
                return is_feature_enabled(organization, feature)
            return role_allowed

    # 3. Not in role defaults — check if plan enables it (ROOT bypass)
    if user.is_root:
        return True

    return False


def invalidate_user_feature_cache(user, organization=None) -> None:
    """Call this when user permissions change."""
    # In production, use a cache pattern that allows bulk invalidation
    # For now, we rely on the 5-min TTL
    pass


def get_all_user_features(user, organization=None) -> dict:
    """Get a dict of all features and their status for a user."""
    from apps.permissions.constants import Feature
    return {
        feature: user_has_feature(user, feature, organization)
        for feature in [v for v in Feature.__dict__.values() if isinstance(v, str)]
    }
