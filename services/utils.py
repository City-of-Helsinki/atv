from django.conf import settings
from rest_framework.exceptions import NotAuthenticated

from atv.exceptions import MissingServiceAPIKey

from .models import Service, ServiceAPIKey


def get_service_from_service_key(request, raise_exception: bool = True) -> Service:
    key = request.META.get(settings.API_KEY_CUSTOM_HEADER)
    service = None

    try:
        if not key:
            raise MissingServiceAPIKey()

        # get_from_key also checks that the key is still valid
        service_key = ServiceAPIKey.objects.get_from_key(key)
        service = service_key.service
    except (
        ServiceAPIKey.DoesNotExist,
        Service.DoesNotExist,
        MissingServiceAPIKey,
    ):
        if raise_exception:
            raise NotAuthenticated()

    return service
