"""Tests for plan limit enforcement."""
import pytest
from apps.plans.services import enforce_plan_limit
from apps.core.exceptions import LicenseLimitExceeded


@pytest.mark.django_db
class TestEnforcePlanLimit:
    def test_raises_when_limit_exceeded(self, org_with_license, end_user_role, user_factory):
        """Fill org to max END_USER limit, then test enforcement."""
        org, license = org_with_license
        limit = license.get_limit_for_role("END_USER")

        # Fill to limit
        from apps.organizations.models import OrganizationMembership
        for i in range(limit):
            user = user_factory(email=f"filler{i}@test.com")
            OrganizationMembership.objects.create(
                user=user, organization=org, role=end_user_role, is_active=True
            )

        # Should now exceed
        with pytest.raises(LicenseLimitExceeded):
            enforce_plan_limit(organization=org, role=end_user_role)

    def test_passes_when_under_limit(self, org_with_license, end_user_role):
        org, license = org_with_license
        # Fresh org — should pass
        enforce_plan_limit(organization=org, role=end_user_role)
