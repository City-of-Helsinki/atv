from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework_api_key.permissions import KeyParser

from services.models import ServiceAPIKey


class ServiceApiKeyAuthentication(BaseAuthentication):
    """Authenticates the user associated with ServiceAPIKey."""

    key_parser = KeyParser()

    def authenticate(self, request):
        key = self.key_parser.get(request)
        if not key:
            return None

        try:
            service_key = ServiceAPIKey.objects.get_from_key(key)
            if service_key.has_expired:
                raise ServiceAPIKey.DoesNotExist()
        except ServiceAPIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("API key is not valid.")

        if not service_key.user:
            raise exceptions.AuthenticationFailed("Permissions missing from API key.")

        return service_key.user, service_key
