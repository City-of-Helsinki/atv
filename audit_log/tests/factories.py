import factory

from audit_log.models import AuditLogEntry


class AuditLogEntryFactory(factory.django.DjangoModelFactory):
    message = {"field": "content"}

    class Meta:
        model = AuditLogEntry
