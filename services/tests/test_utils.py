import pytest
from helusers.authz import UserAuthorization
from rest_framework.exceptions import NotAuthenticated

from services.models import ServiceAPIKey
from services.tests.factories import ServiceClientIdFactory
from services.utils import get_service_from_request


def test_get_service_from_request(rf, user, service):
    sc = ServiceClientIdFactory(service=service)

    request = rf.request()

    # The user is authenticated and has permissions for the service
    request.user = user
    request.auth = UserAuthorization(user, {"azp": sc.client_id})

    request_service = get_service_from_request(request)

    assert request_service == service == request._service


def test_get_service_from_request_not_authenticated(
    rf, settings, anonymous_user, service
):
    request = rf.request()
    service_api_key, key = ServiceAPIKey.objects.create_key(
        service=service,
        name=f"{service.name} api key",
    )
    request.user = service_api_key.user
    request.auth = service_api_key

    request_service = get_service_from_request(request)

    assert request_service == service == request._service


def test_get_service_from_request_superuser_no_service(rf, superuser):
    request = rf.request()
    request.user = superuser
    request.auth = None

    assert get_service_from_request(request) is None


def test_get_service_from_request_no_azp_claim(rf, user):
    request = rf.request()

    # The user is authenticated and has permissions for the service
    request.user = user
    request.auth = UserAuthorization(user, {})

    request_service = get_service_from_request(request, raise_exception=False)

    assert request_service is request._service is None


def test_get_service_from_request_no_azp_claim_raise_exception(rf, user):
    request = rf.request()

    # The user is authenticated and has permissions for the service
    request.user = user
    request.auth = UserAuthorization(user, {})

    with pytest.raises(NotAuthenticated):
        get_service_from_request(request)


def test_get_service_from_request_no_service_client_id(rf, user):
    request = rf.request()

    # The user is authenticated and has permissions for the service
    request.user = user
    request.auth = UserAuthorization(user, {"azp": "another-client-id"})

    request_service = get_service_from_request(request, raise_exception=False)

    assert request_service is request._service is None


def test_get_service_from_request_no_service_client_id_raise_exception(rf, user):
    request = rf.request()

    # The user is authenticated and has permissions for the service
    request.user = user
    request.auth = UserAuthorization(user, {"azp": "another-client-id"})

    with pytest.raises(NotAuthenticated):
        get_service_from_request(request)
