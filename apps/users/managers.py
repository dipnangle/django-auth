"""User model managers."""

from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)

    def verified(self):
        return self.filter(is_email_verified=True, is_deleted=False)

    def with_global_role(self, role_name):
        return self.filter(global_role__name=role_name, is_deleted=False)

    def staff_level(self):
        """ROOT and SUPERADMIN users."""
        return self.filter(global_role__isnull=False, is_deleted=False)


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def active(self):
        return self.get_queryset().active()

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Django admin superuser — different from platform ROOT."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)
        return self.create_user(email, password, **extra_fields)

    # expose queryset methods
    def active(self):
        return self.get_queryset().active()

    def verified(self):
        return self.get_queryset().verified()

    def all_including_deleted(self):
        return UserQuerySet(self.model, using=self._db)
