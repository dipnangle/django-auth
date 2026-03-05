"""
JWT token management.
- Access token: 15 min, stateless
- Refresh token: 7 days, server-side tracked
- Blacklist: Redis-backed for instant revocation
"""

import uuid
import logging
from datetime import datetime, timedelta, timezone as dt_timezone

import jwt
from django.conf import settings
from django.core.cache import caches

from apps.core.exceptions import TokenExpired, TokenInvalid

logger = logging.getLogger(__name__)

# Use a dedicated Redis cache for token blacklist
blacklist_cache = caches["rate_limit"]

JWT_SETTINGS = settings.JWT_SETTINGS


def _get_secret() -> str:
    return JWT_SETTINGS["SIGNING_KEY"]


def _get_algorithm() -> str:
    return JWT_SETTINGS["ALGORITHM"]


# ─────────────────────────────────────────────
# Token Generation
# ─────────────────────────────────────────────

def generate_access_token(user, organization=None) -> str:
    """Generate a short-lived JWT access token."""
    now = datetime.now(dt_timezone.utc)
    expiry = now + timedelta(minutes=JWT_SETTINGS["ACCESS_TOKEN_LIFETIME_MINUTES"])

    payload = {
        "token_type": "access",
        "user_id": str(user.id),
        "email": user.email,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expiry,
        "iss": JWT_SETTINGS["ISSUER"],
        "aud": JWT_SETTINGS["AUDIENCE"],
    }

    if organization:
        payload["org_id"] = str(organization.id)

    if user.global_role:
        payload["role"] = user.global_role.name
        payload["role_level"] = user.global_role.level

    return jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())


def generate_refresh_token(user) -> tuple[str, str]:
    """
    Generate a long-lived refresh token.
    Returns: (encoded_token, jti)
    """
    now = datetime.now(dt_timezone.utc)
    expiry = now + timedelta(days=JWT_SETTINGS["REFRESH_TOKEN_LIFETIME_DAYS"])
    jti = str(uuid.uuid4())

    payload = {
        "token_type": "refresh",
        "user_id": str(user.id),
        "jti": jti,
        "iat": now,
        "exp": expiry,
        "iss": JWT_SETTINGS["ISSUER"],
        "aud": JWT_SETTINGS["AUDIENCE"],
    }

    token = jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())
    return token, jti


def generate_token_pair(user, organization=None) -> dict:
    """Generate both access and refresh tokens. Used on login."""
    access_token = generate_access_token(user, organization)
    refresh_token, jti = generate_refresh_token(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": JWT_SETTINGS["ACCESS_TOKEN_LIFETIME_MINUTES"] * 60,
        "refresh_jti": jti,
    }


# ─────────────────────────────────────────────
# Token Validation
# ─────────────────────────────────────────────

def decode_token(token: str, token_type: str = "access") -> dict:
    """
    Decode and validate a JWT token.
    Raises TokenExpired or TokenInvalid on failure.
    """
    try:
        payload = jwt.decode(
            token,
            _get_secret(),
            algorithms=[_get_algorithm()],
            issuer=JWT_SETTINGS["ISSUER"],
            audience=JWT_SETTINGS["AUDIENCE"],
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpired()
    except jwt.InvalidTokenError as e:
        raise TokenInvalid(f"Token is invalid: {str(e)}")

    if payload.get("token_type") != token_type:
        raise TokenInvalid(f"Expected {token_type} token.")

    # Check blacklist
    jti = payload.get("jti")
    if jti and is_token_blacklisted(jti):
        raise TokenInvalid("Token has been revoked.")

    return payload


def decode_access_token(token: str) -> dict:
    return decode_token(token, token_type="access")


def decode_refresh_token(token: str) -> dict:
    return decode_token(token, token_type="refresh")


# ─────────────────────────────────────────────
# Token Blacklist (Redis)
# ─────────────────────────────────────────────

def blacklist_token(jti: str, expires_in_seconds: int = None) -> None:
    """Add a JTI to the blacklist. Token is immediately invalid."""
    if expires_in_seconds is None:
        expires_in_seconds = JWT_SETTINGS["REFRESH_TOKEN_LIFETIME_DAYS"] * 86400

    blacklist_cache.set(
        f"blacklist:{jti}",
        "1",
        timeout=expires_in_seconds,
    )
    logger.debug("Token blacklisted: %s", jti)


def is_token_blacklisted(jti: str) -> bool:
    """Check if a JTI is in the blacklist."""
    return blacklist_cache.get(f"blacklist:{jti}") is not None


def blacklist_all_user_tokens(user_id: str) -> None:
    """
    Blacklist all tokens for a user by storing a global revocation timestamp.
    Any token issued before this timestamp is considered invalid.
    """
    import time
    blacklist_cache.set(
        f"user_revoke:{user_id}",
        str(time.time()),
        timeout=JWT_SETTINGS["REFRESH_TOKEN_LIFETIME_DAYS"] * 86400,
    )
    logger.info("All tokens revoked for user: %s", user_id)


def is_user_tokens_revoked(user_id: str, issued_at: float) -> bool:
    """Check if user's tokens were mass-revoked after a specific issue time."""
    revoke_ts = blacklist_cache.get(f"user_revoke:{user_id}")
    if revoke_ts:
        return issued_at < float(revoke_ts)
    return False


# ─────────────────────────────────────────────
# Token Rotation (for refresh)
# ─────────────────────────────────────────────

def rotate_refresh_token(refresh_token: str) -> dict:
    """
    Validate old refresh token, blacklist it, issue new pair.
    This is called when the client uses their refresh token.
    """
    payload = decode_refresh_token(refresh_token)
    user_id = payload.get("user_id")
    old_jti = payload.get("jti")
    issued_at = payload.get("iat", 0)

    # Check mass revocation
    if is_user_tokens_revoked(user_id, issued_at):
        raise TokenInvalid("Token has been revoked.")

    # Get user
    from apps.users.selectors import get_user_by_id
    user = get_user_by_id(user_id)

    if not user.is_active or user.is_suspended:
        raise TokenInvalid("User account is not active.")

    # Blacklist old refresh token
    if JWT_SETTINGS.get("BLACKLIST_AFTER_ROTATION", True):
        remaining = payload["exp"] - datetime.now(dt_timezone.utc).timestamp()
        blacklist_token(old_jti, int(max(remaining, 0)))

    return generate_token_pair(user)


def decode_partial_token(token: str) -> dict:
    """Decode the short-lived partial auth token issued during 2FA flow."""
    import jwt
    from django.conf import settings as s
    try:
        payload = jwt.decode(
            token,
            s.JWT_SETTINGS["SIGNING_KEY"],
            algorithms=[s.JWT_SETTINGS["ALGORITHM"]],
            audience=s.JWT_SETTINGS["AUDIENCE"],
            issuer=s.JWT_SETTINGS["ISSUER"],
        )
        if payload.get("token_type") != "2fa_pending":
            raise ValueError("Not a partial auth token")
        return payload
    except Exception as e:
        from apps.core.exceptions import TokenInvalid
        raise TokenInvalid(str(e))
