"""Plan signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="plans.License")
def on_license_change(sender, instance, created, **kwargs):
    """Sync org suspension state when license is suspended."""
    if instance.is_suspended and not instance.organization.is_suspended:
        instance.organization.suspend(reason=instance.suspended_reason)
    elif not instance.is_suspended and instance.organization.is_suspended:
        instance.organization.unsuspend()
