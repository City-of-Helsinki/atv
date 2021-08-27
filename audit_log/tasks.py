import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from elasticsearch import Elasticsearch

from audit_log.models import AuditLogEntry

ES_GOOD_STATUSES = ["created", "updated"]


logger = logging.getLogger(__name__)


def send_audit_log_entries():
    """Send audit logs to Elasticsearch and mark them as sent."""
    if not settings.ENABLE_SEND_AUDIT_LOG:
        logger.info("Sending audit logs not enabled, skipping.")
        return

    if not (
        settings.ELASTICSEARCH_CLOUD_ID
        and settings.ELASTICSEARCH_API_ID
        and settings.ELASTICSEARCH_API_KEY
    ):
        logger.warning(
            "Trying to send audit logs to Elasticsearch without proper configuration, process skipped"
        )
        return

    es = Elasticsearch(
        cloud_id=settings.ELASTICSEARCH_CLOUD_ID,
        api_key=(settings.ELASTICSEARCH_API_ID, settings.ELASTICSEARCH_API_KEY),
    )
    entries = AuditLogEntry.objects.filter(is_sent=False).order_by("created_at")

    for entry in entries.iterator():
        response = es.index(
            index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX,
            id=entry.id,
            body=entry.message,
        )
        if response.get("result") in ES_GOOD_STATUSES:
            AuditLogEntry.objects.filter(pk=entry.pk).update(is_sent=True)

    if count := entries.count():
        logger.info(f"Sent {count} audit logs to elastic search.")


def clear_audit_log_entries(days_to_keep=30):
    """Remove sent audit log entries, which are older than `days_to_keep` days."""
    if not settings.CLEAR_AUDIT_LOG_ENTRIES:
        logger.info("Clearing audit logs not enabled, skipping.")
        return

    sent_entries = AuditLogEntry.objects.filter(
        is_sent=True, created_at__lte=(timezone.now() - timedelta(days=days_to_keep))
    )
    if count := sent_entries.count():
        sent_entries.delete()
        logger.info(
            f"Cleared {count} sent audit logs, which were older than {days_to_keep} days."
        )
