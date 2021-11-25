from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.core.management import call_command
from freezegun import freeze_time

from audit_log.models import AuditLogEntry
from audit_log.tasks import clear_audit_log_entries, send_audit_log_entries


@pytest.mark.parametrize("management_command", [True, False])
@pytest.mark.parametrize(
    "result_value, expected_status",
    [("created", True), ("failed", False)],
)
@pytest.mark.django_db
def test_send_audit_log_success(
    audit_log_entry_factory, settings, result_value, expected_status, management_command
):
    audit_log_entry_factory()

    with mock.patch("elasticsearch.Elasticsearch.index") as elasticsearch_index_mock:
        elasticsearch_index_mock.return_value = {"result": result_value}

        if management_command:
            call_command("send_audit_logs")
        else:
            send_audit_log_entries()

    assert AuditLogEntry.objects.first().is_sent == expected_status


@pytest.mark.parametrize("management_command", [True, False])
@pytest.mark.parametrize(
    "days_since_created,should_delete",
    [(29, False), (30, True), (31, True)],
)
def test_old_audit_logs_are_cleared(
    audit_log_entry_factory, days_since_created, should_delete, management_command
):
    deleted = audit_log_entry_factory(is_sent=True)
    not_deleted = audit_log_entry_factory(is_sent=False)

    dt = datetime.now() + timedelta(days=days_since_created)
    with freeze_time(dt):
        if management_command:
            call_command("clear_audit_logs")
        else:
            clear_audit_log_entries()

    qs = AuditLogEntry.objects.all()
    if should_delete:
        assert deleted not in qs
        assert not_deleted in qs
        assert qs.count() == 1
    else:
        assert deleted in qs
        assert not_deleted in qs
        assert qs.count() == 2
