"""
Custom managers for soft delete pattern.
"""

from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet that excludes soft-deleted records by default."""

    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def soft_delete(self):
        from django.utils import timezone
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def restore(self):
        return self.update(is_deleted=False, deleted_at=None)


class SoftDeleteManager(models.Manager):
    """
    Default manager — automatically excludes soft-deleted records.
    Use this for all normal queries.
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def alive(self):
        return self.get_queryset().alive()

    def deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class AllObjectsManager(models.Manager):
    """
    Manager that includes ALL records, including soft-deleted ones.
    Use: MyModel.all_objects.filter(...)
    Useful for admin panels and data recovery.
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)
