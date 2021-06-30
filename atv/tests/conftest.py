import pytest


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture(autouse=True)
def autouse_django_db(db, django_db_setup, django_db_blocker):
    pass


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    pass
