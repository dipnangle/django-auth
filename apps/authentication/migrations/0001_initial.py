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
            name="BlacklistedToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("jti", models.CharField(db_index=True, max_length=36, unique=True)),
                ("blacklisted_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(db_index=True, blank=True, null=True)),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="users.user")),
            ],
            options={"db_table": "blacklisted_tokens"},
        ),
        migrations.CreateModel(
            name="EmailVerificationToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("token_hash", models.CharField(db_index=True, max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("is_used", models.BooleanField(default=False)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="email_verification_token", to="users.user")),
            ],
            options={"db_table": "email_verification_tokens"},
        ),
        migrations.CreateModel(
            name="PasswordResetToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("token_hash", models.CharField(db_index=True, max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("is_used", models.BooleanField(default=False)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("requested_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="password_reset_tokens", to="users.user")),
            ],
            options={"db_table": "password_reset_tokens"},
        ),
    ]
