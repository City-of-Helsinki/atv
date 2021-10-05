import pytest
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, ValidationError

from atv.exceptions import ATVError, MissingServiceAPIKey, ServiceNotIdentifiedError
from utils.exceptions import (
    custom_exception_handler,
    get_error_response,
    sentry_before_send,
)


@pytest.mark.parametrize(
    "exception_class",
    [ATVError, ServiceNotIdentifiedError, MissingServiceAPIKey],
)
def test_sentry_before_send_exclude_atv_error(exception_class):
    hint = {"exc_info": (exception_class, exception_class("test"), None)}

    assert sentry_before_send("EVENT", hint) is None


@pytest.mark.parametrize(
    "exception_class",
    [ValueError, TypeError, ValidationError, NotAuthenticated],
)
def test_sentry_before_send_dont_exclude_other_errors(exception_class):
    hint = {"exc_info": (exception_class, exception_class("test"), None)}
    event = "EVENT"

    assert sentry_before_send(event, hint) == event


@pytest.mark.parametrize(
    "exception_class",
    [ValueError, TypeError, ValidationError, NotAuthenticated],
)
def test_sentry_before_send_no_exc_info(exception_class):
    hint = {}
    event = "EVENT"

    assert sentry_before_send(event, hint) == event


def test_custom_exception_handler_unknown_exception():
    exc = Exception("Test")
    response = custom_exception_handler(exc)
    body = response.data

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert body == get_error_response(
        "GENERAL_ERROR",
        "Test",
    )
