from django.apps import AppConfig


class PlansConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.plans"
    verbose_name = "Plans"

    def ready(self):
        try:
            import apps.plans.signals  # noqa
        except ImportError:
            pass
