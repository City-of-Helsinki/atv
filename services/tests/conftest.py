import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from services.tests.factories import ServiceAPIKeyFactory, ServiceFactory


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


register(ServiceFactory)
register(ServiceAPIKeyFactory)
