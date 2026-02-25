"""All audit action constants. Import these instead of raw strings."""


class AuditAction:
    # Auth
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_LOGIN_FAILED = "user.login_failed"
    USER_REGISTERED = "user.registered"
    USER_LOCKED = "user.locked"
    USER_UNLOCKED = "user.unlocked"
    EMAIL_VERIFIED = "user.email_verified"
    PASSWORD_CHANGED = "user.password_changed"
    PASSWORD_RESET_REQUESTED = "user.password_reset_requested"
    PASSWORD_RESET_COMPLETED = "user.password_reset_completed"

    # 2FA
    TWO_FA_ENABLED = "2fa.enabled"
    TWO_FA_DISABLED = "2fa.disabled"
    TWO_FA_VERIFIED = "2fa.verified"
    TWO_FA_FAILED = "2fa.failed"
    BACKUP_CODES_GENERATED = "2fa.backup_codes_generated"

    # Users
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_SUSPENDED = "user.suspended"
    USER_UNSUSPENDED = "user.unsuspended"
    USER_DELETED = "user.deleted"
    USER_RESTORED = "user.restored"

    # Roles
    ROLE_ASSIGNED = "role.assigned"
    ROLE_REVOKED = "role.revoked"
    ROLE_CHANGED = "role.changed"

    # Organizations
    ORG_CREATED = "org.created"
    ORG_UPDATED = "org.updated"
    ORG_SUSPENDED = "org.suspended"
    ORG_DELETED = "org.deleted"
    MEMBER_ADDED = "org.member_added"
    MEMBER_REMOVED = "org.member_removed"

    # Invitations
    INVITE_SENT = "invitation.sent"
    INVITE_ACCEPTED = "invitation.accepted"
    INVITE_REVOKED = "invitation.revoked"
    INVITE_EXPIRED = "invitation.expired"

    # Plans & Licenses
    LICENSE_ASSIGNED = "license.assigned"
    LICENSE_UPGRADED = "license.upgraded"
    LICENSE_DOWNGRADED = "license.downgraded"
    LICENSE_SUSPENDED = "license.suspended"
    LICENSE_EXPIRED = "license.expired"

    # Sessions
    SESSION_REVOKED = "session.revoked"
    SESSION_ALL_REVOKED = "session.all_revoked"

    # Impersonation
    IMPERSONATION_STARTED = "impersonation.started"
    IMPERSONATION_ENDED = "impersonation.ended"

    # Permissions
    FEATURE_GRANTED = "permission.feature_granted"
    FEATURE_REVOKED = "permission.feature_revoked"

    # System
    SYSTEM_CONFIG_CHANGED = "system.config_changed"
