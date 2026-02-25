#!/usr/bin/env python
"""
CLI script to create the ROOT user.
This is the ONLY way to create a ROOT user — never via the API.

Usage:
    cd backend
    DJANGO_ENV=production python scripts/create_root_user.py
"""

import os
import sys
import django
import getpass

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def create_root_user():
    from apps.users.models import User
    from apps.roles.models import Role

    print("\n=== CREATE ROOT USER ===\n")

    # Get ROOT role
    try:
        root_role = Role.objects.get(name="ROOT")
    except Role.DoesNotExist:
        print("❌ ROOT role not found. Have you run migrations?")
        print("   Run: python manage.py migrate")
        sys.exit(1)

    # Check if ROOT already exists
    existing = User.objects.filter(global_role=root_role).first()
    if existing:
        print(f"⚠️  ROOT user already exists: {existing.email}")
        confirm = input("Create another ROOT? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            sys.exit(0)

    # Collect credentials
    email = input("Email: ").strip()
    if not email:
        print("❌ Email is required.")
        sys.exit(1)

    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()

    while True:
        password = getpass.getpass("Password (min 10 chars, complex): ")
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("❌ Passwords do not match. Try again.")
        elif len(password) < 10:
            print("❌ Password must be at least 10 characters.")
        else:
            break

    # Create user
    from django.db import transaction
    try:
        with transaction.atomic():
            if User.objects.filter(email__iexact=email).exists():
                print(f"❌ User with email {email} already exists.")
                sys.exit(1)

            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name or "Root",
                last_name=last_name or "User",
                is_email_verified=True,
                is_active=True,
                is_staff=True,
                is_superuser=True,
                is_2fa_enforced=True,
            )
            user.global_role = root_role
            user.save(update_fields=["global_role"])

            print(f"\n✅ ROOT user created successfully!")
            print(f"   Email:    {user.email}")
            print(f"   ID:       {user.id}")
            print(f"\n⚠️  IMPORTANT: Set up 2FA immediately after first login.")
            print(f"              2FA is mandatory for ROOT users.\n")

    except Exception as e:
        print(f"❌ Failed to create ROOT user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_root_user()
