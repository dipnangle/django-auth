"""Audit service — the single function used to log everything."""

import logging
from apps.core.middleware import get_current_request, get_current_org

logger = logging.getLogger(__name__)


def log_action(
    *,
    action: str,
    actor=None,
    target=None,
    organization=None,
    metadata: dict = None,
    status: str = "success",
    request=None,
) -> None:
    """
    Log an audit action.
    Automatically extracts context from the current request if not provided.

    Usage:
        log_action(
            action=AuditAction.USER_CREATED,
            actor=request.user,
            target=new_user,
            metadata={"role": "ADMIN"},
        )
    """
    try:
        from apps.audit.models import AuditLog

        # Auto-extract request context
        if request is None:
            request = get_current_request()

        if organization is None:
            organization = get_current_org()

        # Build actor info
        actor_email = ""
        actor_role = ""
        if actor:
            actor_email = getattr(actor, "email", "") or ""
            role = getattr(actor, "global_role", None)
            actor_role = role.name if role else ""

        # Build target info
        target_type = ""
        target_id = ""
        target_repr = ""
        if target:
            target_type = target.__class__.__name__.lower()
            target_id = str(getattr(target, "id", ""))
            target_repr = str(target)[:255]

        # Extract request metadata
        ip_address = None
        user_agent = ""
        request_id = ""
        if request:
            ip_address = getattr(request, "audit_ip", None)
            user_agent = getattr(request, "audit_user_agent", "")[:512]
            request_id = getattr(request, "id", "")

        AuditLog.objects.create(
            actor=actor,
            actor_email=actor_email,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_repr=target_repr,
            organization=organization,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata or {},
            status=status,
        )
    except Exception as e:
        # Never let audit logging break the main flow
        logger.error("Failed to write audit log for action '%s': %s", action, str(e))
