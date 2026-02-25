"""System configuration — live DB-backed settings."""

from django.db import models
from apps.core.models import BaseModel


class SystemConfig(BaseModel):
    """
    Key-value store for live platform settings.
    ROOT can change these without a redeploy.
    Values are stored as JSON for type flexibility.
    """

    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False, help_text="Mask value in API responses.")
    updated_by = models.ForeignKey("users.User", null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "system_config"
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} = {'***' if self.is_sensitive else self.value}"
