"""Impersonation services."""

import logging
from django.db import transaction
from django.utils import timezone
from apps.core.exceptions import InsufficientRole, PlanFeatureDenied, ResourceNotFound
from apps.core.utils import generate_secure_token

logger = logging.getLogger(__name__)


@transaction.atomic
def start_impersonation(*, impersonator, target, organization=None, reason: str = "", ip: str = "") -> dict:
    """
    Start impersonating another user.
    Issues a special impersonation token (not a regular JWT).
    """
    from apps.impersonation.models import ImpersonationSession
    from apps.roles.hierarchy import can_impersonate
    from apps.plans.selectors import is_feature_enabled
    from apps.audit.services import log_action
    from apps.audit.constants import AuditAction

    # 1. Feature check — impersonation must be enabled on the plan
    if organization and not is_feature_enabled(organization, "impersonation"):
        raise PlanFeatureDenied("Impersonation is not available on your current plan.")

    # 2. Hierarchy check
    if not can_impersonate(impersonator=impersonator, target=target):
        raise InsufficientRole("You do not have permission to impersonate this user.")

    # 3. End any existing impersonation sessions
    ImpersonationSession.objects.filter(impersonator=impersonator, is_active=True).update(
        is_active=False,
        ended_at=timezone.now(),
    )

    token = generate_secure_token(32)
    session = ImpersonationSession.objects.create(
        impersonator=impersonator,
        target=target,
        organization=organization,
        reason=reason,
        impersonation_token=token,
        ip_address=ip,
        is_active=True,
    )

    log_action(
        action=AuditAction.IMPERSONATION_STARTED,
        actor=impersonator,
        target=target,
        organization=organization,
        metadata={"reason": reason, "target_email": target.email},
    )

    # Generate a limited-scope access token for the target user
    from apps.authentication.tokens import generate_access_token
    access_token = generate_access_token(target, organization)

    logger.info("Impersonation started: %s → %s", impersonator.email, target.email)
    return {
        "impersonation_session_id": str(session.id),
        "impersonation_token": token,
        "access_token": access_token,
        "target_user_id": str(target.id),
        "target_email": target.email,
    }


@transaction.atomic
def stop_impersonation(*, impersonator) -> None:
    from apps.impersonation.models import ImpersonationSession
    from apps.audit.services import log_action
    from apps.audit.constants import AuditAction

    sessions = ImpersonationSession.objects.filter(impersonator=impersonator, is_active=True)
    for session in sessions:
        log_action(
            action=AuditAction.IMPERSONATION_ENDED,
            actor=impersonator,
            target=session.target,
            organization=session.organization,
        )

    sessions.update(is_active=False, ended_at=timezone.now())
    logger.info("Impersonation ended: %s", impersonator.email)
