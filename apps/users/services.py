"""
User service layer.
All business logic for user operations lives here.
Views should call these functions, never the ORM directly.
"""

import logging
from django.db import transaction
from django.utils import timezone
from apps.core.exceptions import (
    ResourceNotFound,
    ResourceAlreadyExists,
    ValidationError,
    InsufficientRole,
    LicenseLimitExceeded,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def create_user(
    *,
    email: str,
    first_name: str,
    last_name: str,
    password: str = None,
    phone: str = "",
    created_by=None,
    organization=None,
    role=None,
    send_verification: bool = True,
    is_email_verified: bool = False,
) -> "User":
    """
    Create a new user.
    - Validates email uniqueness
    - Checks plan limits if org is provided
    - Enforces role hierarchy (created_by must outrank role)
    - Sends verification email unless skip_verification=True
    """
    from apps.users.models import User
    from apps.users.selectors import get_user_by_email

    # 1. Email uniqueness check
    if User.all_including_deleted().filter(email__iexact=email).exists():
        raise ResourceAlreadyExists(f"A user with email '{email}' already exists.")

    # 2. Role hierarchy check
    if created_by and role:
        from apps.roles.hierarchy import can_assign_role
        if not can_assign_role(assigner=created_by, target_role=role, organization=organization):
            raise InsufficientRole(
                f"You do not have permission to create a user with role '{role.name}'."
            )

    # 3. Plan limit check
    if organization and role:
        from apps.plans.services import enforce_plan_limit
        enforce_plan_limit(organization=organization, role=role)

    # 4. Create user
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        is_email_verified=is_email_verified,
        is_active=True,
    )

    # 5. Enforce 2FA requirement based on role
    if role:
        from apps.roles.constants import RoleLevel
        if role.level <= RoleLevel.ADMIN:
            user.is_2fa_enforced = True
            user.save(update_fields=["is_2fa_enforced"])

    # 6. Add to organization with role
    if organization and role:
        from apps.organizations.services import add_member_to_organization
        add_member_to_organization(
            organization=organization,
            user=user,
            role=role,
            added_by=created_by,
        )

    # 7. Send verification email (async)
    if send_verification and not is_email_verified:
        from apps.authentication.services import send_verification_email
        send_verification_email(user=user)

    logger.info("User created: %s (by: %s)", user.email, created_by)
    return user


@transaction.atomic
def update_user(*, user, updated_by=None, **fields) -> "User":
    """Update allowed user fields. Validates hierarchy if role-sensitive fields change."""
    from apps.users.models import User

    allowed_fields = {"first_name", "last_name", "phone", "avatar_url"}
    admin_only_fields = {"is_active", "must_change_password"}

    update_fields = []

    for field, value in fields.items():
        if field in allowed_fields:
            setattr(user, field, value)
            update_fields.append(field)
        elif field in admin_only_fields:
            if updated_by and updated_by.get_effective_role_level() > user.get_effective_role_level():
                raise InsufficientRole("Cannot modify this field — target user has equal or higher role.")
            setattr(user, field, value)
            update_fields.append(field)

    if update_fields:
        update_fields.append("updated_at")
        user.save(update_fields=update_fields)

    return user


@transaction.atomic
def deactivate_user(*, user, deactivated_by) -> "User":
    """
    Deactivate (soft disable) a user.
    - Revokes all active sessions
    - Preserves all data
    """
    from apps.roles.hierarchy import can_manage_user
    if not can_manage_user(manager=deactivated_by, target=user):
        raise InsufficientRole("You cannot deactivate this user.")

    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])

    # Revoke all sessions
    from apps.sessions.services import revoke_all_sessions
    revoke_all_sessions(user=user)

    logger.info("User deactivated: %s (by: %s)", user.email, deactivated_by.email)
    return user


@transaction.atomic
def delete_user(*, user, deleted_by) -> None:
    """
    Soft-delete a user.
    - PII is anonymized
    - Data is preserved for audit trail
    """
    from apps.roles.hierarchy import can_manage_user
    if not can_manage_user(manager=deleted_by, target=user):
        raise InsufficientRole("You cannot delete this user.")

    from apps.sessions.services import revoke_all_sessions
    revoke_all_sessions(user=user)

    user.soft_delete()
    logger.info("User soft-deleted: %s (by: %s)", user.id, deleted_by.email)


@transaction.atomic
def change_password(*, user, old_password: str, new_password: str) -> "User":
    """Change user password with old password verification."""
    if not user.check_password(old_password):
        raise ValidationError("Current password is incorrect.")

    from django.contrib.auth.password_validation import validate_password
    validate_password(new_password, user)

    user.set_password(new_password)
    user.password_changed_at = timezone.now()
    user.must_change_password = False
    user.save(update_fields=["password", "password_changed_at", "must_change_password", "updated_at"])

    # Revoke all other sessions (force re-login)
    from apps.sessions.services import revoke_all_sessions
    revoke_all_sessions(user=user)

    return user


@transaction.atomic
def unlock_user(*, user, unlocked_by) -> "User":
    """Manually unlock a locked account."""
    from apps.roles.hierarchy import can_manage_user
    if not can_manage_user(manager=unlocked_by, target=user):
        raise InsufficientRole("You cannot unlock this user.")
    user.unlock()
    return user


@transaction.atomic
def suspend_user(*, user, suspended_by) -> "User":
    """Suspend a user account."""
    from apps.roles.hierarchy import can_manage_user
    if not can_manage_user(manager=suspended_by, target=user):
        raise InsufficientRole("You cannot suspend this user.")
    user.suspend(suspended_by_user=suspended_by)
    from apps.sessions.services import revoke_all_sessions
    revoke_all_sessions(user=user)
    return user
