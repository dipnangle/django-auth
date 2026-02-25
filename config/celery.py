"""
Celery application configuration.

Workers are started via:
    celery -A config worker -l info
    celery -A config beat -l info
"""

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("platform")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "cleanup-expired-sessions": {
        "task": "apps.sessions.tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=2, minute=0),
    },
    "cleanup-expired-audit-logs": {
        "task": "apps.audit.tasks.cleanup_expired_logs",
        "schedule": crontab(hour=3, minute=0),
    },
    "cleanup-expired-tokens": {
        "task": "apps.authentication.tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=4, minute=0),
    },
    "cleanup-expired-invitations": {
        "task": "apps.invitations.tasks.cleanup_expired_invitations",
        "schedule": crontab(hour=4, minute=30),
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
