import uuid

import pytest
from django.conf import settings
from django.utils.module_loading import import_string
from helusers.utils import uuid_to_username
from social_django.models import UserSocialAuth
from social_django.utils import load_backend, load_strategy

from users.models import User
from users.pipeline import store_user_details

# Steps that create the user and the social auth link; the rest need a real OIDC flow
USER_PIPELINE_STEPS = {
    "helusers.pipeline.create_or_update_user",
    "social_core.pipeline.social_auth.associate_user",
    "users.pipeline.store_user_details",
}

RESPONSE_PII = {
    "given_name": "First",
    "family_name": "Last",
    "email": "admin@example.com",
}


def _run_user_pipeline_steps(uid, response):
    backend = load_backend(load_strategy(), "tunnistamo", redirect_uri=None)
    backend.id_token = {}
    kwargs = {
        "backend": backend,
        "uid": uid,
        "response": response,
        "details": {},
        "username": uuid_to_username(uid),
    }
    for step in settings.SOCIAL_AUTH_PIPELINE:
        if step in USER_PIPELINE_STEPS:
            kwargs.update(import_string(step)(**kwargs) or {})


@pytest.mark.django_db
def test_pipeline_keeps_pii_on_first_login():
    uid = str(uuid.uuid4())
    response = {"sub": uid, **RESPONSE_PII}

    _run_user_pipeline_steps(uid, response)

    user = User.objects.get(uuid=uid)
    assert user.social_auth.exists()
    assert user.first_name == "First"
    assert user.last_name == "Last"
    assert user.email == "admin@example.com"
    assert user.get_username() == "admin@example.com"


@pytest.mark.django_db
def test_store_user_details_skips_existing_association(user_factory):
    user = user_factory(first_name="", last_name="", email="")
    UserSocialAuth.objects.create(user=user, provider="tunnistamo", uid=str(user.uuid))

    store_user_details(response=RESPONSE_PII, user=user, new_association=False)

    user.refresh_from_db()
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.email == ""
