from django.contrib import admin
from apps.roles.models import Role, RoleFeaturePermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "is_global", "created_at")
    list_filter = ("is_global",)
    search_fields = ("name",)
    ordering = ("level",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(RoleFeaturePermission)
class RoleFeaturePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "feature", "is_allowed")
    list_filter = ("role", "is_allowed")
    search_fields = ("feature",)
