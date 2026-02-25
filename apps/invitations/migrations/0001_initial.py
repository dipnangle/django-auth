from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("organizations", "0001_initial"),
        ("users", "0001_initial"),
        ("roles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invitation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email", models.EmailField()),
                ("token_hash", models.CharField(db_index=True, max_length=64, unique=True)),
                ("status", models.CharField(
                    choices=[("pending","pending"),("accepted","accepted"),("expired","expired"),("revoked","revoked")],
                    default="pending", max_length=20, db_index=True,
                )),
                ("expires_at", models.DateTimeField()),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("message", models.TextField(blank=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invitations", to="organizations.organization")),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="roles.role")),
                ("invited_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sent_invitations", to="users.user")),
                ("accepted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="accepted_invitations", to="users.user")),
            ],
            options={"db_table": "invitations"},
        ),
    ]
