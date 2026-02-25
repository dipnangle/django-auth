from django.contrib import admin
from apps.two_factor.models import TOTPDevice, BackupCode


@admin.register(TOTPDevice)
class TOTPDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "is_confirmed", "confirmed_at", "last_used_at")
    list_filter = ("is_confirmed",)
    search_fields = ("user__email",)
    readonly_fields = ("id", "secret", "created_at", "updated_at")


@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "used_at", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__email",)
    readonly_fields = ("id", "created_at")
