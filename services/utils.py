from typing import Optional

from rest_framework.exceptions import NotAuthenticated

from services.models import ServiceClientId

from .models import Service, ServiceAPIKey


def get_service_api_key_from_request(request) -> Optional[ServiceAPIKey]:
    """Return API Key if it was used for authentication."""
    return request.auth if isinstance(request.auth, ServiceAPIKey) else None


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

    if api_key := get_service_api_key_from_request(request):
        request._service = api_key.service
    elif not request.user.is_superuser:
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
