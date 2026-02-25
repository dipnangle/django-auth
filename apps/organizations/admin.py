from django.contrib import admin
from apps.organizations.models import Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "is_suspended", "created_at")
    list_filter = ("is_active", "is_suspended", "deployment_mode")
    search_fields = ("name", "slug", "contact_email")
    readonly_fields = ("id", "slug", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "is_active", "joined_at")
    list_filter = ("is_active", "role")
    search_fields = ("user__email", "organization__name")
    readonly_fields = ("id", "joined_at")
