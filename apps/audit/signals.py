"""
Audit signals.
Automatically fires audit log entries on key model changes.
Connect these in apps.py ready() method.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.audit.constants import AuditAction
from apps.core.middleware import get_current_request

logger = logging.getLogger(__name__)


def _get_actor_and_org():
    """Extract actor and org from current request."""
    request = get_current_request()
    if not request:
        return None, None
    actor = getattr(request, "user", None)
    if not actor or not actor.is_authenticated:
        actor = None
    org = getattr(request, "organization", None)
    return actor, org


# ─────────────────────────────────────────────
# User signals
# ─────────────────────────────────────────────

@receiver(post_save, sender="users.User")
def on_user_save(sender, instance, created, **kwargs):
    from apps.audit.services import log_action
    actor, org = _get_actor_and_org()

    if created:
        log_action(
            action=AuditAction.USER_CREATED,
            actor=actor,
            target=instance,
            organization=org,
            metadata={"email": instance.email},
        )


# ─────────────────────────────────────────────
# Organization membership signals
# ─────────────────────────────────────────────

@receiver(post_save, sender="organizations.OrganizationMembership")
def on_membership_save(sender, instance, created, **kwargs):
    from apps.audit.services import log_action
    actor, org = _get_actor_and_org()

    if created:
        log_action(
            action=AuditAction.MEMBER_ADDED,
            actor=actor,
            target=instance.user,
            organization=instance.organization,
            metadata={"role": instance.role.name},
        )
