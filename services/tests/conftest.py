import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from atv.tests.conftest import *  # noqa

from .factories import ServiceAPIKeyFactory, ServiceFactory


@pytest.fixture
def api_client():
    return APIClient()


register(ServiceFactory)
register(ServiceAPIKeyFactory)
