from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("users", "0001_initial"),
        ("roles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("description", models.TextField(blank=True)),
                ("logo_url", models.URLField(blank=True)),
                ("website", models.URLField(blank=True)),
                ("custom_domain", models.CharField(blank=True, max_length=253)),
                ("deployment_mode", models.CharField(choices=[("saas","saas"),("self_hosted","self_hosted")], default="saas", max_length=20)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("is_suspended", models.BooleanField(default=False)),
                ("suspended_at", models.DateTimeField(blank=True, null=True)),
                ("suspended_reason", models.TextField(blank=True)),
                ("contact_email", models.EmailField(blank=True)),
                ("contact_phone", models.CharField(blank=True, max_length=20)),
                ("country", models.CharField(blank=True, max_length=2)),
                ("timezone", models.CharField(default="UTC", max_length=50)),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_organizations", to="users.user",
                )),
            ],
            options={"db_table": "organizations"},
        ),
        migrations.CreateModel(
            name="OrganizationMembership",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="users.user")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="organizations.organization")),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="roles.role")),
                ("added_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="added_members", to="users.user",
                )),
            ],
            options={"db_table": "organization_memberships", "unique_together": {("user", "organization")}},
        ),
    ]
