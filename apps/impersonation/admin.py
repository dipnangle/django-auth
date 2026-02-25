from django.contrib import admin
from apps.impersonation.models import ImpersonationSession


@admin.register(ImpersonationSession)
class ImpersonationSessionAdmin(admin.ModelAdmin):
    list_display = ("impersonator", "target", "organization", "is_active", "started_at", "ended_at")
    list_filter = ("is_active",)
    search_fields = ("impersonator__email", "target__email")
    readonly_fields = ("id", "impersonation_token", "started_at")
    ordering = ("-started_at",)
