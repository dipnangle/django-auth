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
            name="SystemConfig",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("key", models.CharField(max_length=100, unique=True, db_index=True)),
                ("value", models.JSONField()),
                ("description", models.TextField(blank=True)),
                ("is_sensitive", models.BooleanField(default=False)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="users.user")),
            ],
            options={"db_table": "system_config"},
        ),
    ]
