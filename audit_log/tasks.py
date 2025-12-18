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

    if not (settings.ELASTIC_HOST and settings.ELASTIC_AUDIT_LOG_INDEX):
        logger.warning(
            "Trying to send audit logs to Elasticsearch without proper configuration,"
            " process skipped"
        )
        return

    scheme = "https" if settings.ELASTIC_SSL else "http"
    es = Elasticsearch(
        hosts=[f"{scheme}://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"],
        basic_auth=(settings.ELASTIC_USERNAME, settings.ELASTIC_PASSWORD),
    )
    entries = AuditLogEntry.objects.filter(is_sent=False).order_by("created_at")

    if settings.ELASTIC_CREATE_DATA_STREAM:
        es.indices.create_data_stream(name=settings.ELASTIC_AUDIT_LOG_INDEX, ignore=400)

    for entry in entries.iterator():
        # Elastic data stream require @timestamp
        body = {"@timestamp": entry.timestamp, **entry.message}

        response = es.index(
            index=settings.ELASTIC_AUDIT_LOG_INDEX,
            body=body,
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
            f"Cleared {count} sent audit logs, which were older than {days_to_keep}"
            " days."
        )
