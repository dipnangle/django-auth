"""Management command to seed system config defaults."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed default system configuration values into the database."

    def handle(self, *args, **options):
        from apps.system_config.services import seed_defaults
        count = seed_defaults()
        if count:
            self.stdout.write(self.style.SUCCESS(f"✅ Seeded {count} system config entries."))
        else:
            self.stdout.write("ℹ️  All system config entries already exist — nothing to seed.")
