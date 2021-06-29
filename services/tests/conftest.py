import pytest
from django.conf import settings
from pytest_factoryboy import register

from atv.tests.conftest import *  # noqa

from ..models import ServiceAPIKey
from .factories import ServiceAPIKeyFactory, ServiceFactory


@pytest.fixture
def service_api_client(api_client):
    service = ServiceFactory()
    service_api_key, key = ServiceAPIKey.objects.create_key(
        service=service, name=f"{service.name} api key"
    )

    credentials = {settings.API_KEY_CUSTOM_HEADER: key}
    api_client.credentials(**credentials)
    return api_client


register(ServiceFactory)
register(ServiceAPIKeyFactory)
