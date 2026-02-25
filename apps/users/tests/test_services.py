"""Tests for user services."""
import pytest
from apps.users.services import create_user
from apps.core.exceptions import ResourceAlreadyExists


@pytest.mark.django_db
class TestCreateUser:
    def test_creates_user_successfully(self):
        user = create_user(
            email="newuser@example.com",
            first_name="New",
            last_name="User",
            password="SecurePass123!",
            send_verification=False,
            is_email_verified=True,
        )
        assert user.email == "newuser@example.com"
        assert user.pk is not None

    def test_raises_on_duplicate_email(self):
        create_user(
            email="dup@example.com",
            first_name="A", last_name="B",
            send_verification=False,
        )
        with pytest.raises(ResourceAlreadyExists):
            create_user(
                email="dup@example.com",
                first_name="C", last_name="D",
                send_verification=False,
            )

    def test_email_is_case_insensitive(self):
        create_user(
            email="Case@Example.com",
            first_name="A", last_name="B",
            send_verification=False,
        )
        with pytest.raises(ResourceAlreadyExists):
            create_user(
                email="case@example.com",
                first_name="C", last_name="D",
                send_verification=False,
            )
