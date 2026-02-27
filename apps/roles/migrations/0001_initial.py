from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=50, unique=True)),
                ("level", models.PositiveSmallIntegerField(db_index=True)),
                ("description", models.TextField(blank=True)),
                ("is_global", models.BooleanField(default=False)),
            ],
            options={"db_table": "roles", "ordering": ["level"]},
        ),
        migrations.CreateModel(
            name="RoleFeaturePermission",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("feature", models.CharField(max_length=100)),
                ("is_allowed", models.BooleanField(default=True)),
                ("role", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="feature_permissions", to="roles.role")),
            ],
            options={"db_table": "role_feature_permissions", "unique_together": {("role", "feature")}},
        ),
    ]
