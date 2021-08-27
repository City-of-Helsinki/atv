from django.core.management.base import BaseCommand

from audit_log.tasks import send_audit_log_entries


class Command(BaseCommand):
    help = "Send unsent audit log entries to Elasticsearch"

    def handle(self, *args, **kwargs):
        send_audit_log_entries()
