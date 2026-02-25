"""Seed default roles on first migration."""

from django.db import migrations


ROLES = [
    {"name": "ROOT", "level": 0, "description": "Platform developer. God-level access. CLI only.", "is_global": True},
    {"name": "SUPERADMIN", "level": 10, "description": "Platform/org owner. Manages everything.", "is_global": True},
    {"name": "ADMIN_PLUS", "level": 20, "description": "Senior manager. Creates admins and users.", "is_global": False},
    {"name": "ADMIN", "level": 30, "description": "Basic manager. Creates end users only.", "is_global": False},
    {"name": "END_USER", "level": 40, "description": "General consumer.", "is_global": False},
]


def seed_roles(apps, schema_editor):
    Role = apps.get_model("roles", "Role")
    for role_data in ROLES:
        Role.objects.get_or_create(name=role_data["name"], defaults=role_data)


def reverse_roles(apps, schema_editor):
    Role = apps.get_model("roles", "Role")
    Role.objects.filter(name__in=[r["name"] for r in ROLES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("roles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, reverse_roles),
    ]
