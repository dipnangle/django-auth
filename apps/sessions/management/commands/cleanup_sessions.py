"""Management command to clean up expired sessions."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Remove sessions that expired more than 90 days ago."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=90, help="Sessions older than N days past expiry.")
        parser.add_argument("--dry-run", action="store_true", help="Show count without deleting.")

    def handle(self, *args, **options):
        from django.utils import timezone
        from datetime import timedelta
        from apps.sessions.models import UserSession

        cutoff = timezone.now() - timedelta(days=options["days"])
        qs = UserSession.objects.filter(expires_at__lt=cutoff)

        if options["dry_run"]:
            self.stdout.write(f"Would delete {qs.count()} sessions (dry run).")
            return

        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted} expired sessions."))
