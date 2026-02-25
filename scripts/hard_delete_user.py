#!/usr/bin/env python
"""
CLI script to permanently (hard) delete a user from the database.
Only for GDPR/legal erasure requests — normally use soft delete.

Usage:
    DJANGO_ENV=production python scripts/hard_delete_user.py <user_id_or_email>
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def hard_delete_user(identifier: str):
    from apps.users.models import User

    print(f"\n=== HARD DELETE USER: {identifier} ===\n")

    # Find user
    try:
        import uuid
        uuid.UUID(identifier)
        user = User.all_including_deleted().filter(id=identifier).first()
    except ValueError:
        user = User.all_including_deleted().filter(email__iexact=identifier).first()

    if not user:
        print(f"❌ User not found: {identifier}")
        sys.exit(1)

    print(f"User found:")
    print(f"  ID:      {user.id}")
    print(f"  Email:   {user.email}")
    print(f"  Name:    {user.full_name}")
    print(f"  Deleted: {user.is_deleted}")
    print()
    print("⚠️  WARNING: This will PERMANENTLY delete all user data.")
    print("   This cannot be undone. Use only for GDPR erasure requests.")
    print()

    confirm = input(f"Type the user's email to confirm deletion: ").strip()
    if confirm != user.email:
        print("❌ Email did not match. Aborted.")
        sys.exit(1)

    final_confirm = input("Are you absolutely sure? (type 'DELETE'): ").strip()
    if final_confirm != "DELETE":
        print("Aborted.")
        sys.exit(0)

    from django.db import transaction
    try:
        with transaction.atomic():
            user_id = str(user.id)
            user_email = user.email

            # Clean up related records
            from apps.sessions.models import UserSession
            from apps.authentication.models import BlacklistedToken, EmailVerificationToken, PasswordResetToken
            from apps.two_factor.models import TOTPDevice, BackupCode
            from apps.impersonation.models import ImpersonationSession
            from apps.audit.models import AuditLog

            deleted_sessions = UserSession.objects.filter(user=user).delete()[0]
            deleted_tokens = BlacklistedToken.objects.filter(user=user).delete()[0]
            EmailVerificationToken.objects.filter(user=user).delete()
            PasswordResetToken.objects.filter(user=user).delete()
            TOTPDevice.objects.filter(user=user).delete()
            BackupCode.objects.filter(user=user).delete()

            # Nullify audit log actor (preserve log entries, anonymize actor)
            AuditLog.objects.filter(actor=user).update(actor=None, actor_email=f"[deleted:{user_id}]")

            # Hard delete the user
            user.hard_delete() if hasattr(user, "hard_delete") else user.delete()

            print(f"\n✅ User permanently deleted: {user_email} ({user_id})")
            print(f"   Sessions deleted:        {deleted_sessions}")
            print(f"   Tokens deleted:          {deleted_tokens}")

    except Exception as e:
        print(f"❌ Failed to delete user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/hard_delete_user.py <user_id_or_email>")
        sys.exit(1)

    hard_delete_user(sys.argv[1])
