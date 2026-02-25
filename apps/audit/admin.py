from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor_email", "actor_role", "target_type", "target_repr", "status", "organization", "created_at")
    list_filter = ("action", "status", "target_type")
    search_fields = ("actor_email", "target_repr", "action")
    readonly_fields = tuple(f.name for f in AuditLog._meta.fields)  # all readonly
    ordering = ("-created_at",)

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
