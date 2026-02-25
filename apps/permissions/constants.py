"""All feature flag strings. Central registry for the entire platform."""


class Feature:
    # ── User management ──────────────────────
    USER_CREATE = "user.create"
    USER_READ = "user.read"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_LIST_ALL = "user.list_all"
    USER_ASSIGN_ROLE = "user.assign_role"
    USER_SUSPEND = "user.suspend"
    USER_UNLOCK = "user.unlock"

    # ── Dashboard ────────────────────────────
    DASHBOARD_VIEW = "dashboard.view"
    DASHBOARD_ANALYTICS = "dashboard.analytics"

    # ── Reports ──────────────────────────────
    REPORTS_VIEW = "reports.view"
    REPORTS_EXPORT = "reports.export"

    # ── Settings ─────────────────────────────
    SETTINGS_VIEW = "settings.view"
    SETTINGS_MANAGE = "settings.manage"

    # ── 2FA ──────────────────────────────────
    TWO_FA_ENFORCE = "2fa.enforce"
    TWO_FA_BYPASS = "2fa.bypass"  # ROOT only

    # ── API access ───────────────────────────
    API_ACCESS = "api.access"

    # ── Impersonation ────────────────────────
    IMPERSONATION = "impersonation"

    # ── Organization ─────────────────────────
    ORG_MANAGE = "org.manage"
    ORG_VIEW_ALL = "org.view_all"

    # ── Audit logs ───────────────────────────
    AUDIT_VIEW = "audit.view"
    AUDIT_EXPORT = "audit.export"

    # ── Future apps register their flags here ─
    # CRM
    CRM_CONTACTS_READ = "crm.contacts.read"
    CRM_CONTACTS_WRITE = "crm.contacts.write"
    CRM_DEALS_READ = "crm.deals.read"
    CRM_DEALS_WRITE = "crm.deals.write"
    CRM_REPORTS = "crm.reports"


# Default feature sets per role — seeded to RoleFeaturePermission
ROLE_DEFAULT_FEATURES = {
    "ROOT": [f for f in Feature.__dict__.values() if isinstance(f, str)],  # All features
    "SUPERADMIN": [
        Feature.USER_CREATE, Feature.USER_READ, Feature.USER_UPDATE,
        Feature.USER_DELETE, Feature.USER_LIST_ALL, Feature.USER_ASSIGN_ROLE,
        Feature.USER_SUSPEND, Feature.USER_UNLOCK,
        Feature.DASHBOARD_VIEW, Feature.DASHBOARD_ANALYTICS,
        Feature.REPORTS_VIEW, Feature.REPORTS_EXPORT,
        Feature.SETTINGS_VIEW, Feature.SETTINGS_MANAGE,
        Feature.TWO_FA_ENFORCE,
        Feature.API_ACCESS,
        Feature.ORG_MANAGE, Feature.ORG_VIEW_ALL,
        Feature.AUDIT_VIEW, Feature.AUDIT_EXPORT,
        Feature.IMPERSONATION,
    ],
    "ADMIN_PLUS": [
        Feature.USER_CREATE, Feature.USER_READ, Feature.USER_UPDATE,
        Feature.USER_DELETE, Feature.USER_LIST_ALL, Feature.USER_ASSIGN_ROLE,
        Feature.USER_SUSPEND, Feature.USER_UNLOCK,
        Feature.DASHBOARD_VIEW, Feature.DASHBOARD_ANALYTICS,
        Feature.REPORTS_VIEW, Feature.REPORTS_EXPORT,
        Feature.SETTINGS_VIEW,
        Feature.AUDIT_VIEW,
        Feature.API_ACCESS,
    ],
    "ADMIN": [
        Feature.USER_CREATE, Feature.USER_READ, Feature.USER_UPDATE,
        Feature.USER_LIST_ALL,
        Feature.DASHBOARD_VIEW,
        Feature.REPORTS_VIEW,
        Feature.AUDIT_VIEW,
    ],
    "END_USER": [
        Feature.DASHBOARD_VIEW,
        Feature.USER_READ,
    ],
}
