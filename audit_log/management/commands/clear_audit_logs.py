from django.core.management.base import BaseCommand

from audit_log.tasks import clear_audit_log_entries


class Command(BaseCommand):
    help = "Clear old sent audit log entries from database"

    def handle(self, *args, **kwargs):
        clear_audit_log_entries()
