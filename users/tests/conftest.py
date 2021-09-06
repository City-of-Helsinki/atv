import pytest
from pytest_factoryboy import register

from .factories import UserFactory


@pytest.fixture
def superuser(user):
    user.is_superuser = True
    user.save()
    return user


register(UserFactory)
