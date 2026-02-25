from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("jti", models.CharField(db_index=True, max_length=36, unique=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("device_type", models.CharField(blank=True, max_length=20)),
                ("browser", models.CharField(blank=True, max_length=50)),
                ("os", models.CharField(blank=True, max_length=50)),
                ("location_country", models.CharField(blank=True, max_length=2)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("last_active_at", models.DateTimeField(auto_now=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_reason", models.CharField(blank=True, max_length=100)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="users.user")),
            ],
            options={"db_table": "user_sessions", "ordering": ["-last_active_at"]},
        ),
    ]
