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
            name="ImpersonationSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("started_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("reason", models.TextField(blank=True)),
                ("impersonation_token", models.CharField(max_length=64, unique=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("impersonator", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="impersonation_sessions", to="users.user")),
                ("target", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="impersonated_sessions", to="users.user")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="organizations.organization")),
            ],
            options={"db_table": "impersonation_sessions", "ordering": ["-started_at"]},
        ),
    ]
