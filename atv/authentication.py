from django.core.cache import cache
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

        # Check if key has been recently verified
        if service_key := cache.get(str(key)):
            return service_key.user, service_key

        try:
            service_key = ServiceAPIKey.objects.get_from_key(key)
            if service_key.has_expired:
                raise ServiceAPIKey.DoesNotExist()
        except ServiceAPIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("API key is not valid.")

        if not service_key.user:
            raise exceptions.AuthenticationFailed("Permissions missing from API key.")

        # Verified key is cached for 5 minutes. This improves subsequent requests' response times significantly.
        # Default cache uses local memory caching. Keys aren't accessible from console or to other threads or pods
        # TODO: if caching is refactored to use Redis or Memcached this needs to be reconsidered
        cache.set(key, service_key, timeout=60 * 5)

        return service_key.user, service_key
