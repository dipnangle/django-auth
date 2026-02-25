"""Tests for JWT token generation and validation."""
import pytest
import time
from apps.authentication.tokens import (
    generate_access_token, generate_refresh_token,
    decode_access_token, decode_refresh_token,
    blacklist_token, is_token_blacklisted,
)
from apps.core.exceptions import TokenExpired, TokenInvalid


@pytest.mark.django_db
class TestJWTTokens:
    def test_generate_access_token(self, user_factory):
        user = user_factory()
        token = generate_access_token(user)
        assert isinstance(token, str)
        assert len(token) > 50

    def test_decode_access_token(self, user_factory):
        user = user_factory()
        token = generate_access_token(user)
        payload = decode_access_token(token)
        assert payload["user_id"] == str(user.id)
        assert payload["token_type"] == "access"

    def test_generate_refresh_token(self, user_factory):
        user = user_factory()
        token, jti = generate_refresh_token(user)
        assert isinstance(token, str)
        assert isinstance(jti, str)
        assert len(jti) == 36  # UUID length

    def test_decode_refresh_token(self, user_factory):
        user = user_factory()
        token, jti = generate_refresh_token(user)
        payload = decode_refresh_token(token)
        assert payload["jti"] == jti

    def test_blacklisted_token_raises(self, user_factory):
        user = user_factory()
        token = generate_access_token(user)
        payload = decode_access_token(token)
        blacklist_token(payload["jti"])
        with pytest.raises(TokenInvalid):
            decode_access_token(token)

    def test_wrong_type_raises(self, user_factory):
        user = user_factory()
        refresh_token, _ = generate_refresh_token(user)
        with pytest.raises(TokenInvalid):
            decode_access_token(refresh_token)  # Should fail — wrong type
