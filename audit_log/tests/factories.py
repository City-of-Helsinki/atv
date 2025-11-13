import factory
from resilient_logger.models import ResilientLogEntry


class AuditLogEntryFactory(factory.django.DjangoModelFactory):
    message = {"field": "content"}

    class Meta:
        model = ResilientLogEntry
