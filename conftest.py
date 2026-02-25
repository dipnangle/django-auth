"""
Global pytest fixtures.
All tests share these — no need to import, pytest auto-discovers conftest.py
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


# ─────────────────────────────────────────────
# Role fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def role_factory():
    """Return a role by name. Roles are seeded via migrations."""
    def _get_role(name: str):
        from apps.roles.models import Role
        return Role.objects.get(name=name)
    return _get_role


@pytest.fixture
def end_user_role(role_factory):
    return role_factory("END_USER")


@pytest.fixture
def admin_role(role_factory):
    return role_factory("ADMIN")


@pytest.fixture
def admin_plus_role(role_factory):
    return role_factory("ADMIN_PLUS")


@pytest.fixture
def superadmin_role(role_factory):
    return role_factory("SUPERADMIN")


@pytest.fixture
def root_role(role_factory):
    return role_factory("ROOT")


# ─────────────────────────────────────────────
# User fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def user_factory():
    """Factory to create users with custom attributes."""
    def _create_user(email=None, password="TestPass123!", role=None, **kwargs):
        import uuid
        email = email or f"user_{uuid.uuid4().hex[:8]}@test.com"
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=kwargs.pop("first_name", "Test"),
            last_name=kwargs.pop("last_name", "User"),
            **kwargs,
        )
        if role:
            user.global_role = role
            user.save(update_fields=["global_role"])
        return user
    return _create_user


@pytest.fixture
def verified_user_factory(user_factory):
    """Factory for email-verified users."""
    def _create(email=None, password="TestPass123!", **kwargs):
        return user_factory(
            email=email,
            password=password,
            is_email_verified=True,
            **kwargs,
        )
    return _create


@pytest.fixture
def root_user(user_factory, root_role):
    return user_factory(
        email="root@platform.com",
        is_email_verified=True,
        role=root_role,
    )


@pytest.fixture
def superadmin_user(user_factory, superadmin_role):
    return user_factory(
        email="superadmin@test.com",
        is_email_verified=True,
        role=superadmin_role,
    )


@pytest.fixture
def admin_user(user_factory, admin_role):
    return user_factory(
        email="admin@test.com",
        is_email_verified=True,
        role=admin_role,
    )


@pytest.fixture
def end_user(user_factory, end_user_role):
    return user_factory(
        email="enduser@test.com",
        is_email_verified=True,
        role=end_user_role,
    )


# ─────────────────────────────────────────────
# Organization fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def organization_factory():
    def _create(name="Test Org", **kwargs):
        from apps.organizations.models import Organization
        import uuid
        return Organization.objects.create(
            name=name,
            slug=f"test-org-{uuid.uuid4().hex[:6]}",
            **kwargs,
        )
    return _create


@pytest.fixture
def organization(organization_factory):
    return organization_factory()


@pytest.fixture
def org_with_license(organization_factory):
    """Returns (org, license) tuple with a Basic plan."""
    from apps.plans.models import Plan, License
    from django.utils import timezone

    org = organization_factory(name="Licensed Org")

    plan, _ = Plan.objects.get_or_create(
        tier="basic",
        defaults={
            "name": "Basic",
            "max_superadmins": 1,
            "max_admin_plus": 2,
            "max_admins": 5,
            "max_end_users": 10,
            "features_json": [],
        }
    )

    license = License.objects.create(
        organization=org,
        plan=plan,
        is_active=True,
        valid_from=timezone.now(),
    )
    return org, license


# ─────────────────────────────────────────────
# API client fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(api_client, verified_user_factory):
    """Authenticated API client as a regular verified user."""
    from apps.authentication.tokens import generate_access_token
    user = verified_user_factory()
    token = generate_access_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    api_client.user = user
    return api_client


@pytest.fixture
def admin_api_client(api_client, user_factory, admin_role):
    """Authenticated API client as an ADMIN."""
    from apps.authentication.tokens import generate_access_token
    user = user_factory(
        email="admin_client@test.com",
        is_email_verified=True,
        role=admin_role,
    )
    token = generate_access_token(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    api_client.user = user
    return api_client


@pytest.fixture
def root_api_client(api_client, root_user):
    """Authenticated API client as ROOT."""
    from apps.authentication.tokens import generate_access_token
    token = generate_access_token(root_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    api_client.user = root_user
    return api_client
