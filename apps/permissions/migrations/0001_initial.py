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
            name="UserPermissionOverride",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("feature", models.CharField(max_length=100)),
                ("is_granted", models.BooleanField(default=True)),
                ("reason", models.TextField(blank=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="permission_overrides", to="users.user")),
                ("granted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="granted_permissions", to="users.user")),
            ],
            options={"db_table": "user_permission_overrides", "unique_together": {("user", "feature")}},
        ),
    ]
