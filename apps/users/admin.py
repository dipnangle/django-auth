from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "global_role", "is_active", "is_2fa_enabled", "created_at")
    list_filter = ("is_active", "is_2fa_enabled", "is_2fa_enforced", "global_role")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at", "last_login_at", "last_login_ip", "password_changed_at")
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "phone_number", "avatar_url")}),
        ("Role & Auth", {"fields": ("global_role", "is_active", "is_email_verified", "is_2fa_enabled", "is_2fa_enforced", "must_change_password")}),
        ("Lockout", {"fields": ("failed_login_attempts", "locked_until")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "last_login_at", "last_login_ip", "password_changed_at")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "first_name", "last_name")}),
    )
