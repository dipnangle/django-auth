"""Tests for role hierarchy enforcement."""
import pytest
from apps.roles.hierarchy import can_assign_role, can_manage_user
from apps.roles.constants import RoleLevel


@pytest.mark.django_db
class TestCanAssignRole:
    def test_root_can_assign_any_role(self, root_user, role_factory):
        for role_name in ["SUPERADMIN", "ADMIN_PLUS", "ADMIN", "END_USER"]:
            role = role_factory(role_name)
            assert can_assign_role(assigner=root_user, target_role=role) is True

    def test_admin_can_only_assign_end_user(self, admin_user, role_factory):
        end_user_role = role_factory("END_USER")
        admin_role = role_factory("ADMIN")
        assert can_assign_role(assigner=admin_user, target_role=end_user_role) is True
        assert can_assign_role(assigner=admin_user, target_role=admin_role) is False

    def test_end_user_cannot_assign_any_role(self, end_user, role_factory):
        for role_name in ["ADMIN", "END_USER"]:
            role = role_factory(role_name)
            assert can_assign_role(assigner=end_user, target_role=role) is False

    def test_cannot_assign_own_level(self, superadmin_user, role_factory):
        superadmin_role = role_factory("SUPERADMIN")
        assert can_assign_role(assigner=superadmin_user, target_role=superadmin_role) is False


@pytest.mark.django_db
class TestCanManageUser:
    def test_admin_cannot_manage_superadmin(self, admin_user, superadmin_user):
        assert can_manage_user(manager=admin_user, target=superadmin_user) is False

    def test_superadmin_can_manage_admin(self, superadmin_user, admin_user):
        assert can_manage_user(manager=superadmin_user, target=admin_user) is True

    def test_root_can_manage_everyone(self, root_user, admin_user, end_user):
        assert can_manage_user(manager=root_user, target=admin_user) is True
        assert can_manage_user(manager=root_user, target=end_user) is True
