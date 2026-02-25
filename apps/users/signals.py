"""User signals — post-save hooks."""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="users.User")
def on_user_created(sender, instance, created, **kwargs):
    """Enforce 2FA requirement based on role after user creation."""
    if not created:
        return
    from apps.roles.constants import RoleLevel
    if instance.global_role and instance.global_role.level <= RoleLevel.ADMIN:
        if not instance.is_2fa_enforced:
            instance.is_2fa_enforced = True
            instance.save(update_fields=["is_2fa_enforced"])
