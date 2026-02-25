"""Invitation selectors."""

from django.utils import timezone
from apps.invitations.models import Invitation
from apps.core.utils import hash_token


def get_invitation_by_id(invitation_id: str):
    """Get invitation by UUID."""
    from apps.core.exceptions import NotFound
    try:
        return Invitation.objects.select_related(
            "organization", "role", "invited_by", "accepted_by"
        ).get(id=invitation_id)
    except Invitation.DoesNotExist:
        raise NotFound("Invitation not found.")


def get_invitation_by_token(raw_token: str):
    """Get invitation by raw token (hashes it first)."""
    from apps.core.exceptions import NotFound, ValidationError
    token_hash = hash_token(raw_token)
    try:
        inv = Invitation.objects.select_related(
            "organization", "role", "invited_by"
        ).get(token_hash=token_hash)
    except Invitation.DoesNotExist:
        raise NotFound("Invitation not found or already used.")

    if inv.status != Invitation.Status.PENDING:
        raise ValidationError(f"Invitation is {inv.status}.")
    if inv.is_expired:
        inv.status = Invitation.Status.EXPIRED
        inv.save(update_fields=["status"])
        raise ValidationError("Invitation has expired.")

    return inv


def list_organization_invitations(organization, status=None):
    """List invitations for an organization."""
    qs = Invitation.objects.filter(organization=organization).select_related("role", "invited_by")
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-created_at")


def list_pending_invitations(organization):
    return list_organization_invitations(organization, status=Invitation.Status.PENDING)
