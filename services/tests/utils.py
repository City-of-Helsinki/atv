from helusers.authz import UserAuthorization
from rest_framework.test import APIClient

from services.tests.factories import ServiceClientIdFactory


def get_user_service_client(user, service) -> APIClient:
    """Get an API client with logged in user for a service."""
    sc = ServiceClientIdFactory(service=service)
    api_client = APIClient()
    api_client.force_authenticate(user, UserAuthorization(user, {"azp": sc.client_id}))
    return api_client
