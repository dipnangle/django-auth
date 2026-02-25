from django.apps import AppConfig


class InvitationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.invitations"
    verbose_name = "Invitations"

    def ready(self):
        try:
            import apps.invitations.signals  # noqa
        except ImportError:
            pass
