"""
BaseModel — every model in the system inherits from this.
Provides: UUID primary key, timestamps, soft delete, org scoping.
"""

import uuid
from django.db import models
from django.utils import timezone
from .managers import SoftDeleteManager, AllObjectsManager


class BaseModel(models.Model):
    """
    Abstract base for all models.
    - UUID pk (not sequential, safe for public exposure)
    - created_at / updated_at auto-timestamps
    - Soft delete (is_deleted + deleted_at)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Default manager excludes soft-deleted records
    objects = SoftDeleteManager()
    # Use this when you explicitly need deleted records too
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def soft_delete(self, deleted_by=None):
        """Mark as deleted without removing from DB."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self):
        """Permanently remove from DB. Use with extreme caution."""
        super().delete()


class TenantScopedModel(BaseModel):
    """
    Extends BaseModel with mandatory organization FK.
    All tenant-specific data must inherit from this.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )

    class Meta:
        abstract = True

    @classmethod
    def for_organization(cls, org_id):
        """Shortcut to filter by organization."""
        return cls.objects.filter(organization_id=org_id)
