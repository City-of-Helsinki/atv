import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from atv.tests.factories import GroupFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_client(api_client, user):
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client


@pytest.fixture
def superuser_api_client(api_client, superuser):
    api_client.force_authenticate(user=superuser)
    return api_client


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(autouse=True)
def autouse_django_db(db, django_db_setup, django_db_blocker):
    pass


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    pass


register(GroupFactory)
