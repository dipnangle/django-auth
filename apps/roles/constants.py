"""Role level constants. Lower number = higher privilege."""


class RoleLevel:
    ROOT = 0
    SUPERADMIN = 10
    ADMIN_PLUS = 20
    ADMIN = 30
    END_USER = 40

    CHOICES = [
        (ROOT, "ROOT"),
        (SUPERADMIN, "SUPERADMIN"),
        (ADMIN_PLUS, "ADMIN_PLUS"),
        (ADMIN, "ADMIN"),
        (END_USER, "END_USER"),
    ]

    # Roles that require mandatory 2FA
    MANDATORY_2FA_LEVELS = {ROOT, SUPERADMIN, ADMIN_PLUS, ADMIN}

    # Roles that are global (not org-scoped)
    GLOBAL_ROLE_LEVELS = {ROOT, SUPERADMIN}

    @classmethod
    def name_from_level(cls, level: int) -> str:
        mapping = {v: k for k, v in cls.CHOICES}
        return dict(cls.CHOICES).get(level, "UNKNOWN")

    @classmethod
    def all_names(cls):
        return [name for _, name in cls.CHOICES]
