"""Invitation services."""

import logging
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from apps.core.exceptions import (
    InvitationExpired, InvitationAlreadyUsed, InsufficientRole,
    ResourceNotFound, LicenseLimitExceeded,
)
from apps.core.utils import generate_secure_token, hash_token

logger = logging.getLogger(__name__)


@transaction.atomic
def send_invitation(*, invited_by, organization, role, email: str, message: str = "") -> "Invitation":
    """
    Send an invite email to join an organization.
    Creates an Invitation record with a token-hashed link.
    """
    from apps.invitations.models import Invitation
    from apps.roles.hierarchy import can_assign_role
    from apps.plans.services import enforce_plan_limit
    from apps.notifications.services import send_email

    # 1. Hierarchy check
    if not can_assign_role(assigner=invited_by, target_role=role, organization=organization):
        raise InsufficientRole(f"You cannot invite users with role '{role.name}'.")

    # 2. Plan limit check (count pending invites + existing users)
    enforce_plan_limit(organization=organization, role=role)

    # 3. Check for pending invite to same email in same org
    existing = Invitation.objects.filter(
        email__iexact=email,
        organization=organization,
        status=Invitation.Status.PENDING,
    ).first()
    if existing and not existing.is_expired:
        raise ResourceNotFound(
            f"An active invitation already exists for {email} in this organization."
        )

    # 4. Create invitation
    raw_token = generate_secure_token(48)
    token_hash = hash_token(raw_token)
    expiry_hours = settings.INVITATION["TOKEN_EXPIRY_HOURS"]
    expires_at = timezone.now() + timedelta(hours=expiry_hours)

    invite = Invitation.objects.create(
        organization=organization,
        role=role,
        email=email,
        invited_by=invited_by,
        token_hash=token_hash,
        expires_at=expires_at,
        message=message,
        status=Invitation.Status.PENDING,
    )

    # 5. Send email
    frontend_url = settings.PLATFORM["FRONTEND_URL"]
    invite_url = f"{frontend_url}/invite?token={raw_token}"

    send_email(
        to=email,
        template="invitation",
        context={
            "invited_by": invited_by,
            "organization": organization,
            "role": role,
            "invite_url": invite_url,
            "expires_hours": expiry_hours,
            "message": message,
        },
    )

    logger.info("Invitation sent: %s → %s (%s)", invited_by.email, email, role.name)
    return invite


@transaction.atomic
def accept_invitation(
    *,
    token: str,
    first_name: str,
    last_name: str,
    password: str,
) -> dict:
    """
    Accept an invitation.
    Creates the user account and adds them to the org.
    Returns login tokens.
    """
    from apps.invitations.models import Invitation
    from apps.users.services import create_user
    from apps.authentication.tokens import generate_token_pair

    token_hash = hash_token(token)
    try:
        invite = Invitation.objects.select_related("organization", "role", "invited_by").get(
            token_hash=token_hash,
            status=Invitation.Status.PENDING,
        )
    except Invitation.DoesNotExist:
        raise ResourceNotFound("Invalid invitation link.")

    if invite.is_expired:
        invite.status = Invitation.Status.EXPIRED
        invite.save(update_fields=["status"])
        raise InvitationExpired()

    # Create user
    user = create_user(
        email=invite.email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        created_by=invite.invited_by,
        organization=invite.organization,
        role=invite.role,
        send_verification=False,
        is_email_verified=True,  # Invite link = email confirmed
    )

    # Mark invite as accepted
    invite.status = Invitation.Status.ACCEPTED
    invite.accepted_at = timezone.now()
    invite.accepted_by = user
    invite.save(update_fields=["status", "accepted_at", "accepted_by_id"])

    logger.info("Invitation accepted: %s joined %s as %s", user.email, invite.organization.name, invite.role.name)

    tokens = generate_token_pair(user)
    return {"user_id": str(user.id), "email": user.email, **tokens}


@transaction.atomic
def revoke_invitation(*, invitation_id: str, revoked_by) -> None:
    from apps.invitations.models import Invitation
    from apps.roles.hierarchy import can_manage_user

    try:
        invite = Invitation.objects.get(id=invitation_id, status=Invitation.Status.PENDING)
    except Invitation.DoesNotExist:
        raise ResourceNotFound("Invitation not found or already used.")

    invite.status = Invitation.Status.REVOKED
    invite.save(update_fields=["status"])
    logger.info("Invitation revoked: %s (by: %s)", invite.email, revoked_by.email)


def get_invitation_by_token(token: str) -> "Invitation":
    from apps.invitations.models import Invitation
    token_hash = hash_token(token)
    try:
        return Invitation.objects.select_related("organization", "role", "invited_by").get(
            token_hash=token_hash,
        )
    except Invitation.DoesNotExist:
        raise ResourceNotFound("Invalid invitation link.")
