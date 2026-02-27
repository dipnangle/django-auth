"""
Custom DRF authentication backend.
Validates JWT tokens and loads the user on every request.
"""

import logging
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication

#from apps.core.exceptions import TokenExpired, TokenInvalid, AuthenticationFailed

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    DRF authentication class that validates JWT access tokens.
    Extracts user from token and attaches to request.
    """

    keyword = "Bearer"

    def authenticate(self, request):

        from apps.core.exceptions import TokenExpired, TokenInvalid, AuthenticationFailed

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith(f"{self.keyword} "):
            return None  # Not a JWT request — let other authenticators try

        token = auth_header.split(" ", 1)[1].strip()

        try:
            return self._authenticate_token(token)
        except (TokenExpired, TokenInvalid) as e:
            raise e
        except Exception as e:
            logger.exception("Unexpected error during JWT authentication")
            return None

    def _authenticate_token(self, token: str):
        from apps.authentication.tokens import decode_access_token
        from apps.users.selectors import get_user_by_id

        payload = decode_access_token(token)

        # Check user-level mass revocation
        from apps.authentication.tokens import is_user_tokens_revoked
        if is_user_tokens_revoked(payload["user_id"], payload.get("iat", 0)):
            raise TokenInvalid("Token has been revoked.")

        user = get_user_by_id(payload["user_id"])

        if not user.is_active or user.is_deleted:
            raise TokenInvalid("User account is not active.")

        return (user, token)

    def authenticate_header(self, request):
        return self.keyword


class EmailAuthBackend(ModelBackend):
    """
    Django auth backend that authenticates using email instead of username.
    Used for Django admin login.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        from apps.users.models import User
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        return user.is_active and user.is_staff and not user.is_deleted
