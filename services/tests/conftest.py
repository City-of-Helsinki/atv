import pytest
from pytest_factoryboy import register

from services.tests.factories import ServiceAPIKeyFactory, ServiceFactory


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


register(ServiceFactory)
register(ServiceAPIKeyFactory)
