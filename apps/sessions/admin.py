from django.contrib import admin
from apps.sessions.models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "device_type", "browser", "os", "ip_address", "is_active", "last_active_at", "expires_at")
    list_filter = ("is_active", "device_type")
    search_fields = ("user__email", "ip_address")
    readonly_fields = ("id", "jti", "created_at")
    ordering = ("-last_active_at",)
