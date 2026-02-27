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
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("action", models.CharField(db_index=True, max_length=100)),
                ("actor_email", models.EmailField(blank=True)),
                ("actor_role", models.CharField(blank=True, max_length=50)),
                ("target_type", models.CharField(blank=True, db_index=True, max_length=100)),
                ("target_id", models.CharField(blank=True, db_index=True, max_length=36)),
                ("target_repr", models.CharField(blank=True, max_length=255)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("request_id", models.CharField(blank=True, max_length=36)),
                ("metadata", models.JSONField(default=dict)),
                ("status", models.CharField(
                    choices=[("success","success"),("failure","failure"),("warning","warning")],
                    default="success", max_length=20,
                )),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="users.user")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="organizations.organization")),
            ],
            options={"db_table": "audit_logs", "ordering": ["-created_at"]},
        ),
    ]
