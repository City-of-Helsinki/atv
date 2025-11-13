import logging
from datetime import datetime, timezone
from typing import cast

from django.db import migrations, models


def migrate_to_resilient_logger(apps, schema_editor):
    audit_log_entry = cast(
        type[models.Model], apps.get_model("audit_log", "AuditLogEntry")
    )
    resilient_log_entry = cast(
        type[models.Model], apps.get_model("resilient_logger", "ResilientLogEntry")
    )

    for entry in audit_log_entry.objects.filter(is_sent=False):
        entry_id = entry.id
        is_sent = entry.is_sent
        message = entry.message
        created_at = cast(datetime, entry.created_at).astimezone(timezone.utc)
        audit_event = message["audit_event"]

        resilient_log_entry.objects.create(
            is_sent=is_sent,
            level=logging.NOTSET,
            message=audit_event["status"],
            context={
                "actor": audit_event["actor"],
                "operation": audit_event["operation"],
                "target": audit_event["target"],
                "status": audit_event["status"],
                "orig_entry_id": entry_id,
                "orig_created_at": created_at.isoformat().replace("+00:00", "Z"),
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("audit_log", "0002_add_explicit_plural"),
        ("resilient_logger", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            migrate_to_resilient_logger,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
