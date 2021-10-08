import pytest
from django.contrib.auth.models import AnonymousUser
from pytest_factoryboy import register

from .factories import UserFactory


@pytest.fixture
def superuser(user):
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


register(UserFactory)
