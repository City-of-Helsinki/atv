from datetime import datetime, timezone
from typing import Callable

import factory.random
import pytest
from pytest_factoryboy import register

from atv.tests.conftest import *  # noqa
from audit_log.tests.factories import AuditLogEntryFactory
from users.tests.conftest import *  # noqa


@pytest.fixture(autouse=True)
def setup_deterministic_randomness(settings):
    factory.random.reseed_random("123")


@pytest.fixture
def fixed_datetime() -> Callable[[], datetime]:
    return lambda: datetime(2020, 6, 1, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def setup_audit_logging(settings):
    settings.USE_X_FORWARDED_FOR = True


register(AuditLogEntryFactory)
