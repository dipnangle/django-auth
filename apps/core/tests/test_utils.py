"""Tests for core utilities."""
import pytest
from apps.core.utils import (
    generate_secure_token, hash_token, mask_email,
    mask_phone, chunk_list, safe_get
)


class TestTokenGeneration:
    def test_generate_secure_token_length(self):
        token = generate_secure_token(32)
        assert len(token) > 0

    def test_generate_secure_token_unique(self):
        t1 = generate_secure_token()
        t2 = generate_secure_token()
        assert t1 != t2

    def test_hash_token_consistent(self):
        token = "mysecrettoken"
        assert hash_token(token) == hash_token(token)

    def test_hash_token_different_inputs(self):
        assert hash_token("abc") != hash_token("xyz")


class TestMasking:
    def test_mask_email_standard(self):
        result = mask_email("user@example.com")
        assert "@example.com" in result
        assert result.startswith("us")
        assert "***" in result or "*" in result

    def test_mask_email_short_local(self):
        result = mask_email("a@b.com")
        assert "@b.com" in result

    def test_mask_phone(self):
        result = mask_phone("+1234567890")
        assert result.startswith("+12")
        assert "*" in result


class TestHelpers:
    def test_chunk_list_even(self):
        result = chunk_list([1, 2, 3, 4], 2)
        assert result == [[1, 2], [3, 4]]

    def test_chunk_list_uneven(self):
        result = chunk_list([1, 2, 3], 2)
        assert result == [[1, 2], [3]]

    def test_chunk_list_empty(self):
        assert chunk_list([], 5) == []

    def test_safe_get_nested(self):
        d = {"a": {"b": {"c": 42}}}
        assert safe_get(d, "a", "b", "c") == 42

    def test_safe_get_missing(self):
        d = {"a": 1}
        assert safe_get(d, "x", "y", default="fallback") == "fallback"
