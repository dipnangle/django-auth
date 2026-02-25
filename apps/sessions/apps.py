from django.apps import AppConfig


class SessionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sessions"
    verbose_name = "Sessions"

    def ready(self):
        try:
            import apps.sessions.signals  # noqa
        except ImportError:
            pass
