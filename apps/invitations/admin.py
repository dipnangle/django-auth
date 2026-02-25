from django.contrib import admin
from apps.invitations.models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "organization", "role", "status", "invited_by", "expires_at", "created_at")
    list_filter = ("status", "role")
    search_fields = ("email", "organization__name")
    readonly_fields = ("id", "token_hash", "created_at", "updated_at", "accepted_at")
    ordering = ("-created_at",)
