"""Tests for User model."""
import pytest
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_deleted is False

    def test_full_name_fallback(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="noname@example.com", password="pass"
        )
        assert user.full_name == "noname@example.com"

    def test_is_locked_false_when_no_lockout(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="user@example.com", password="pass"
        )
        assert user.is_locked is False

    def test_is_locked_true_when_locked(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="locked@example.com", password="pass"
        )
        user.locked_until = timezone.now() + timedelta(minutes=30)
        user.save()
        assert user.is_locked is True

    def test_soft_delete_anonymizes_pii(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="real@example.com",
            password="pass",
            first_name="Real",
            last_name="Name",
            phone="+1234567890",
        )
        user.soft_delete()
        assert user.is_deleted is True
        assert user.is_active is False
        assert "deleted" in user.email
        assert user.first_name == "Deleted"
        assert user.phone == ""

    def test_record_login_resets_failures(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="user2@example.com", password="pass"
        )
        user.failed_login_attempts = 3
        user.save()
        user.record_login("127.0.0.1")
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.last_login_ip == "127.0.0.1"
