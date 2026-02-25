from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("organizations", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("tier", models.CharField(choices=[("basic","basic"),("pro","pro"),("premium","premium"),("enterprise","enterprise")], max_length=20)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("price_monthly_usd", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("price_yearly_usd", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("max_superadmins", models.PositiveIntegerField(default=1)),
                ("max_admin_plus", models.PositiveIntegerField(default=2)),
                ("max_admins", models.PositiveIntegerField(default=5)),
                ("max_end_users", models.PositiveIntegerField(default=20)),
                ("features", models.JSONField(default=list)),
                ("audit_log_retention_days", models.PositiveIntegerField(default=30)),
                ("allow_custom_domain", models.BooleanField(default=False)),
                ("allow_api_access", models.BooleanField(default=False)),
                ("allow_impersonation", models.BooleanField(default=False)),
                ("allow_self_hosted", models.BooleanField(default=False)),
                ("enforce_2fa", models.BooleanField(default=False)),
            ],
            options={"db_table": "plans"},
        ),
        migrations.CreateModel(
            name="License",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("valid_from", models.DateField()),
                ("valid_until", models.DateField(blank=True, null=True)),
                ("is_trial", models.BooleanField(default=False)),
                ("grace_period_ends_at", models.DateTimeField(blank=True, null=True)),
                ("is_suspended", models.BooleanField(default=False)),
                ("suspended_reason", models.TextField(blank=True)),
                ("override_max_superadmins", models.PositiveIntegerField(blank=True, null=True)),
                ("override_max_admin_plus", models.PositiveIntegerField(blank=True, null=True)),
                ("override_max_admins", models.PositiveIntegerField(blank=True, null=True)),
                ("override_max_end_users", models.PositiveIntegerField(blank=True, null=True)),
                ("override_features", models.JSONField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="licenses", to="organizations.organization")),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="plans.plan")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="users.user")),
            ],
            options={"db_table": "licenses"},
        ),
        migrations.CreateModel(
            name="LicenseHistory",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("action", models.CharField(max_length=50)),
                ("notes", models.TextField(blank=True)),
                ("snapshot", models.JSONField(default=dict)),
                ("license", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history", to="plans.license")),
                ("changed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="users.user")),
            ],
            options={"db_table": "license_history"},
        ),
    ]
