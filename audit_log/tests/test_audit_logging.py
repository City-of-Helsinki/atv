from datetime import datetime, timezone

import pytest
from django.contrib.auth.models import AnonymousUser
from freezegun import freeze_time
from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources import ResilientLogSource

from audit_log import audit_logging
from audit_log.enums import Operation, Status


@freeze_time("2020-06-01T00:00:00.000Z")
class TestAuditLogging:
    def test_log_origin(self, user):
        audit_logging.log(user, "", Operation.READ, user)

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["origin"] == "atv"

    @freeze_time("2020-06-06T00:00:00Z")
    def test_log_current_timestamp(self, user):
        logging_datetime = datetime.now(tz=timezone.utc)
        audit_logging.log(user, "", Operation.READ, user)

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        logged_date_from_date_time = datetime.strptime(
            audit_doc["audit_event"]["date_time"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        assert logging_datetime == logged_date_from_date_time

    def test_log_actor_uuid(self, fixed_datetime, user, user_factory, snapshot):
        other_user = user_factory()
        audit_logging.log(
            user,
            "",
            Operation.READ,
            other_user,
            ip_address="192.168.1.1",
        )

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["actor"]["user_id"] == str(user.uuid)
        snapshot.assert_match(audit_doc)

    @pytest.mark.parametrize("operation", list(Operation))
    def test_log_owner_operation(self, fixed_datetime, user, operation, snapshot):
        audit_logging.log(user, "", operation, user, ip_address="192.168.1.1")

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["actor"]["role"] == "OWNER"
        snapshot.assert_match(audit_doc)

    @pytest.mark.parametrize("operation", list(Operation))
    def test_log_user_operation(
        self, fixed_datetime, user, user_factory, operation, snapshot
    ):
        other_user = user_factory()

        audit_logging.log(
            user,
            "",
            operation,
            other_user,
            ip_address="192.168.1.1",
        )

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["actor"]["role"] == "USER"
        snapshot.assert_match(audit_doc)

    @pytest.mark.parametrize("operation", list(Operation))
    def test_log_admin_operation(
        self, fixed_datetime, user, user_factory, operation, snapshot
    ):
        other_user = user_factory()

        user.is_superuser = True
        user.save()

        audit_logging.log(
            user,
            "",
            operation,
            other_user,
            ip_address="192.168.1.1",
        )

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["actor"]["role"] == "ADMIN"
        snapshot.assert_match(audit_doc)

    @pytest.mark.parametrize("operation", list(Operation))
    def test_log_system_operation(self, fixed_datetime, user, operation, snapshot):
        audit_logging.log(None, "", operation, user, ip_address="192.168.1.1")

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["actor"]["role"] == "SYSTEM"
        snapshot.assert_match(audit_doc)

    @pytest.mark.parametrize("operation", list(Operation))
    def test_log_anonymous_role(self, fixed_datetime, user, operation, snapshot):
        audit_logging.log(
            AnonymousUser(),
            "",
            operation,
            user,
            ip_address="192.168.1.1",
        )

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["actor"]["role"] == "ANONYMOUS"
        snapshot.assert_match(audit_doc)

    @pytest.mark.parametrize("status", list(Status))
    def test_log_status(self, fixed_datetime, user, status, snapshot):
        audit_logging.log(
            user,
            "",
            Operation.READ,
            user,
            status,
            ip_address="192.168.1.1",
        )

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["message"] == status.value
        assert audit_doc["audit_event"]["extra"]["status"] == status.value
        snapshot.assert_match(audit_doc)

    def test_log_additional_information(self, user):
        audit_logging.log(
            user,
            "",
            Operation.UPDATE,
            user,
            additional_information="test",
        )

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["extra"]["additional_information"] == "test"

    def test_log_user_with_backend(self, user, fixed_datetime, snapshot):
        backend_str = "some.auth.Backend"

        audit_logging.log(
            user,
            "some.auth.Backend",
            Operation.READ,
            user,
            ip_address="192.168.1.1",
        )

        log = ResilientLogEntry.objects.first()
        audit_doc = ResilientLogSource(log).get_document()
        assert audit_doc["audit_event"]["actor"]["provider"] == backend_str
        snapshot.assert_match(audit_doc)
