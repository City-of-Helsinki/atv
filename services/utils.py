from typing import Optional

from django.conf import settings
from rest_framework.exceptions import NotAuthenticated

from atv.exceptions import MissingServiceAPIKey
from services.models import ServiceClientId

from .models import Service, ServiceAPIKey


def get_service_from_service_key(request, raise_exception: bool = True) -> Service:
    key = request.META.get(settings.API_KEY_CUSTOM_HEADER)
    service = None

    try:
        if not key:
            raise MissingServiceAPIKey()

        # get_from_key also checks that the key is still valid
        service_key = ServiceAPIKey.objects.get_from_key(key)

        if service_key.has_expired:
            raise ServiceAPIKey.DoesNotExist()

        service = service_key.service
    except (
        ServiceAPIKey.DoesNotExist,
        Service.DoesNotExist,
        MissingServiceAPIKey,
    ):
        if raise_exception:
            raise NotAuthenticated()

    return service


def get_service_from_request(
    request, raise_exception: bool = True
) -> Optional[Service]:
    """Return the service for the request.

    Unauthenticated calls will identify the service using ServiceAPIKey.
    Authenticated calls will check the azp claim of the auth token to
    see if the client id has been mapped to a service using ServiceClientId.

    Value is cached so the logic will only run once per request.
    """

    if hasattr(request, "_service"):
        return request._service

    request._service = None

    if not request.user.is_authenticated:
        request._service = get_service_from_service_key(
            request, raise_exception=raise_exception
        )

    if not request.user.is_superuser:
        if auth := getattr(request, "auth", None):
            if client_id := auth.data.get("azp"):
                service_client_id = (
                    ServiceClientId.objects.select_related("service")
                    .filter(client_id=client_id)
                    .first()
                )
                if service_client_id:
                    request._service = service_client_id.service

        if not request._service and raise_exception:
            raise NotAuthenticated()

    return request._service
