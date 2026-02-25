from django.contrib import admin
from apps.authentication.models import BlacklistedToken, EmailVerificationToken, PasswordResetToken


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "jti", "blacklisted_at", "expires_at")
    search_fields = ("user__email", "jti")
    readonly_fields = ("id", "blacklisted_at")


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "expires_at", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__email",)
    readonly_fields = ("id", "created_at")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "expires_at", "requested_ip", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__email",)
    readonly_fields = ("id", "created_at")
