from django.contrib import admin
from apps.permissions.models import UserPermissionOverride


@admin.register(UserPermissionOverride)
class UserPermissionOverrideAdmin(admin.ModelAdmin):
    list_display = ("user", "feature", "is_granted", "granted_by", "created_at")
    list_filter = ("is_granted",)
    search_fields = ("user__email", "feature")
    readonly_fields = ("id", "created_at", "updated_at")
