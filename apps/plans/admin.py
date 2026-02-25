from django.contrib import admin
from apps.plans.models import Plan, License, LicenseHistory


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "is_active", "price_monthly_usd")
    list_filter = ("tier", "is_active")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("organization", "plan", "is_active", "is_trial", "valid_from", "valid_until", "is_suspended")
    list_filter = ("is_active", "is_trial", "is_suspended")
    search_fields = ("organization__name",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(LicenseHistory)
class LicenseHistoryAdmin(admin.ModelAdmin):
    list_display = ("license", "action", "changed_by", "created_at")
    readonly_fields = ("id", "created_at")
