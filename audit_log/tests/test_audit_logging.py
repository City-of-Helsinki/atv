from datetime import datetime, timezone

import pytest
from django.contrib.auth.models import AnonymousUser
from freezegun import freeze_time

from audit_log import audit_logging
from audit_log.enums import Operation, Status
from audit_log.models import AuditLogEntry


def test_log_origin(user):
    audit_logging.log(user, "", Operation.READ, user)

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["origin"] == "atv"


@freeze_time("2020-06-01T00:00:00Z")
def test_log_current_timestamp(user):
    logging_datetime = datetime.now(tz=timezone.utc)
    audit_logging.log(user, "", Operation.READ, user)

    message = AuditLogEntry.objects.first().message
    logged_date_from_date_time_epoch = datetime.fromtimestamp(
        int(message["audit_event"]["date_time_epoch"]) / 1000, tz=timezone.utc
    )
    assert logging_datetime == logged_date_from_date_time_epoch
    logged_date_from_date_time = datetime.strptime(
        message["audit_event"]["date_time"], "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    assert logging_datetime == logged_date_from_date_time


def test_log_actor_uuid(fixed_datetime, user, user_factory, snapshot):
    other_user = user_factory()
    audit_logging.log(
        user,
        "",
        Operation.READ,
        other_user,
        get_time=fixed_datetime,
        ip_address="192.168.1.1",
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["actor"]["user_id"] == str(user.uuid)
    snapshot.assert_match(message)


@pytest.mark.parametrize("operation", list(Operation))
def test_log_owner_operation(fixed_datetime, user, operation, snapshot):
    audit_logging.log(
        user, "", operation, user, get_time=fixed_datetime, ip_address="192.168.1.1"
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["actor"]["role"] == "OWNER"
    snapshot.assert_match(message)


@pytest.mark.parametrize("operation", list(Operation))
def test_log_user_operation(fixed_datetime, user, user_factory, operation, snapshot):
    other_user = user_factory()

    audit_logging.log(
        user,
        "",
        operation,
        other_user,
        get_time=fixed_datetime,
        ip_address="192.168.1.1",
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["actor"]["role"] == "USER"
    snapshot.assert_match(message)


@pytest.mark.parametrize("operation", list(Operation))
def test_log_system_operation(fixed_datetime, user, operation, snapshot):
    audit_logging.log(
        None, "", operation, user, get_time=fixed_datetime, ip_address="192.168.1.1"
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["actor"]["role"] == "SYSTEM"
    snapshot.assert_match(message)


@pytest.mark.parametrize("operation", list(Operation))
def test_log_anonymous_role(fixed_datetime, user, operation, snapshot):
    audit_logging.log(
        AnonymousUser(),
        "",
        operation,
        user,
        get_time=fixed_datetime,
        ip_address="192.168.1.1",
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["actor"]["role"] == "ANONYMOUS"
    snapshot.assert_match(message)


@pytest.mark.parametrize("status", list(Status))
def test_log_status(fixed_datetime, user, status, snapshot):
    audit_logging.log(
        user,
        "",
        Operation.READ,
        user,
        status,
        get_time=fixed_datetime,
        ip_address="192.168.1.1",
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["status"] == status.value
    snapshot.assert_match(message)


def test_log_additional_information(user):
    audit_logging.log(
        user,
        "",
        Operation.UPDATE,
        user,
        additional_information="test",
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["additional_information"] == "test"


def test_log_user_with_backend(user, fixed_datetime, snapshot):
    backend_str = "some.auth.Backend"

    audit_logging.log(
        user,
        "some.auth.Backend",
        Operation.READ,
        user,
        get_time=fixed_datetime,
        ip_address="192.168.1.1",
    )

    message = AuditLogEntry.objects.first().message
    assert message["audit_event"]["actor"]["provider"] == backend_str
    snapshot.assert_match(message)
