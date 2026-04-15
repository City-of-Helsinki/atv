import pytest
from social_django.models import UserSocialAuth

from users.models import User

PII_KWARGS = {
    "first_name": "First",
    "last_name": "Last",
    "email": "user@example.com",
}


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def _assert_pii_stripped(user):
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.email == ""


def _assert_pii_kept(user):
    assert user.first_name == PII_KWARGS["first_name"]
    assert user.last_name == PII_KWARGS["last_name"]
    assert user.email == PII_KWARGS["email"]


def test_clean_strips_pii_for_regular_user(user_factory):
    user = user_factory(**PII_KWARGS)
    user.clean()
    _assert_pii_stripped(user)


def test_clean_keeps_pii_for_staff_user(user_factory):
    user = user_factory(is_staff=True, **PII_KWARGS)
    user.clean()
    _assert_pii_kept(user)


def test_clean_keeps_pii_for_superuser(user_factory):
    user = user_factory(is_superuser=True, **PII_KWARGS)
    user.clean()
    _assert_pii_kept(user)


def test_clean_keeps_pii_for_user_with_social_auth(user_factory):
    user = user_factory()
    UserSocialAuth.objects.create(user=user, provider="tunnistamo", uid=str(user.uuid))
    user.first_name = PII_KWARGS["first_name"]
    user.last_name = PII_KWARGS["last_name"]
    user.email = PII_KWARGS["email"]
    user.clean()
    _assert_pii_kept(user)


def test_clean_strips_pii_for_unsaved_user():
    user = User(username="unsaved", **PII_KWARGS)
    # No pk yet, and no social_auth -> PII should be stripped.
    assert user.pk is None
    user.clean()
    _assert_pii_stripped(user)


@pytest.mark.parametrize(
    "flags",
    [
        {"is_staff": True, "is_superuser": True},
        {"is_staff": True},
        {"is_superuser": True},
    ],
)
def test_clean_keeps_pii_for_privileged_users(user_factory, flags):
    user = user_factory(**flags, **PII_KWARGS)
    user.clean()
    _assert_pii_kept(user)
