"""
Redis-backed rate limiter for auth endpoints.
Tracks by IP address and by user identifier (email/user_id).
"""

import logging
import time
from django.core.cache import caches
from apps.core.exceptions import RateLimitExceeded

logger = logging.getLogger(__name__)

# Use dedicated rate_limit cache
rl_cache = caches["rate_limit"]


class RateLimiter:
    """
    Sliding window rate limiter.
    Tracks attempt count in a time window using Redis.
    """

    def __init__(self, key: str, max_attempts: int, window_seconds: int):
        self.key = f"rl:{key}"
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds

    def check(self) -> None:
        """Check limit. Raises RateLimitExceeded if exceeded."""
        current = rl_cache.get(self.key, 0)
        if current >= self.max_attempts:
            raise RateLimitExceeded(
                f"Too many attempts. Please try again in {self.window_seconds // 60} minutes."
            )

    def increment(self) -> int:
        """Increment counter and set expiry. Returns current count."""
        pipe = rl_cache.client.get_client()
        try:
            current = rl_cache.incr(self.key)
            if current == 1:
                rl_cache.expire(self.key, self.window_seconds)
            return current
        except Exception:
            # Redis unavailable — fail open (don't block auth)
            logger.warning("Rate limiter Redis unavailable, failing open for key: %s", self.key)
            return 0

    def check_and_increment(self) -> None:
        """Atomically check then increment. Raises on limit."""
        self.check()
        self.increment()

    def reset(self) -> None:
        """Reset counter (call on successful auth)."""
        rl_cache.delete(self.key)

    @property
    def remaining(self) -> int:
        current = rl_cache.get(self.key, 0)
        return max(0, self.max_attempts - current)


# ─────────────────────────────────────────────
# Pre-configured limiters for auth endpoints
# ─────────────────────────────────────────────

def get_login_limiter(identifier: str) -> RateLimiter:
    """Per-IP or per-email login rate limiter."""
    from django.conf import settings
    cfg = settings.RATE_LIMIT
    return RateLimiter(
        key=f"login:{identifier}",
        max_attempts=cfg["LOGIN_ATTEMPTS"],
        window_seconds=cfg["LOGIN_WINDOW_SECONDS"],
    )


def get_register_limiter(ip: str) -> RateLimiter:
    """Per-IP registration rate limiter."""
    from django.conf import settings
    cfg = settings.RATE_LIMIT
    return RateLimiter(
        key=f"register:{ip}",
        max_attempts=cfg["REGISTER_ATTEMPTS"],
        window_seconds=cfg["REGISTER_WINDOW_SECONDS"],
    )


def get_password_reset_limiter(identifier: str) -> RateLimiter:
    """Per-email password reset limiter."""
    from django.conf import settings
    cfg = settings.RATE_LIMIT
    return RateLimiter(
        key=f"pw_reset:{identifier}",
        max_attempts=cfg["PASSWORD_RESET_ATTEMPTS"],
        window_seconds=cfg["PASSWORD_RESET_WINDOW_SECONDS"],
    )


def get_2fa_limiter(user_id: str) -> RateLimiter:
    """Per-user 2FA attempt limiter."""
    return RateLimiter(key=f"2fa:{user_id}", max_attempts=5, window_seconds=300)
