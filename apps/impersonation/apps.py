from django.apps import AppConfig


class ImpersonationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.impersonation"
    verbose_name = "Impersonation"

    def ready(self):
        try:
            import apps.impersonation.signals  # noqa
        except ImportError:
            pass
