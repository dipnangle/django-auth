"""Impersonation selectors."""

from apps.impersonation.models import ImpersonationSession


def get_active_impersonation(impersonator):
    """Get current active impersonation session for impersonator."""
    return ImpersonationSession.objects.filter(
        impersonator=impersonator, is_active=True
    ).select_related("target", "organization").first()


def get_impersonation_by_token(token: str):
    """Get impersonation session by token."""
    return ImpersonationSession.objects.filter(
        impersonation_token=token, is_active=True
    ).select_related("impersonator", "target").first()


def list_impersonation_history(organization=None, impersonator=None, limit=50):
    """List impersonation audit history."""
    qs = ImpersonationSession.objects.select_related("impersonator", "target", "organization")
    if organization:
        qs = qs.filter(organization=organization)
    if impersonator:
        qs = qs.filter(impersonator=impersonator)
    return qs.order_by("-started_at")[:limit]
