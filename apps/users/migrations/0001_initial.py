from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("roles", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("email", models.EmailField(max_length=254, unique=True, db_index=True)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("avatar_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_email_verified", models.BooleanField(default=False)),
                ("is_suspended", models.BooleanField(default=False, db_index=True)),
                ("suspended_at", models.DateTimeField(blank=True, null=True)),
                ("is_2fa_enabled", models.BooleanField(default=False)),
                ("is_2fa_enforced", models.BooleanField(default=False)),
                ("must_change_password", models.BooleanField(default=False)),
                ("failed_login_attempts", models.PositiveIntegerField(default=0)),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
                ("password_changed_at", models.DateTimeField(blank=True, null=True)),
                ("last_login_at", models.DateTimeField(blank=True, null=True)),
                ("last_login_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("global_role", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="users", to="roles.role",
                )),
                ("suspended_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="suspended_users", to="users.user",
                )),
                ("groups", models.ManyToManyField(
                    blank=True, related_name="user_set",
                    related_query_name="user", to="auth.group",
                    verbose_name="groups",
                )),
                ("user_permissions", models.ManyToManyField(
                    blank=True, related_name="user_set",
                    related_query_name="user", to="auth.permission",
                    verbose_name="user permissions",
                )),
            ],
            options={"db_table": "users", "ordering": ["-created_at"]},
        ),
    ]
