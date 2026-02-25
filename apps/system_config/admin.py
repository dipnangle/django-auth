from django.contrib import admin
from apps.system_config.models import SystemConfig


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "masked_value", "description", "updated_by", "updated_at")
    search_fields = ("key",)
    readonly_fields = ("id", "updated_at")

    def masked_value(self, obj):
        return "***" if obj.is_sensitive else str(obj.value)[:80]
    masked_value.short_description = "Value"
